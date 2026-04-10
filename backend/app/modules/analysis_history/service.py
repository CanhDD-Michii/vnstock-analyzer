"""
Luồng phân tích end-to-end khi user gọi POST /analysis/{ticker}
(STOCK_ANALYSIS_STRATEGY §42 — Data → chỉ số → score → OpenAI → lưu DB).

Nguyên tắc CODE_RULES: orchestration ở service; engine thuần tính toán ở modules.indicators;
AI chỉ luận giải trên payload đã có, không bịa số.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import StockNotFoundError
from app.db.models import AiPromptConfig, User
from app.modules.ai_analysis.client import call_openai_analysis
from app.modules.ai_analysis.prompt_builder import (
    DEFAULT_SYSTEM_PROMPT,
    build_user_message,
)
from app.modules.analysis_history.repository import AnalysisHistoryRepository
from app.modules.indicators.engine_completeness import is_missing_value
from app.modules.indicators.fundamental import compute_fundamental_score
from app.modules.indicators.fundamental_context import build_fundamental_context
from app.modules.indicators.fundamental_metrics_merge import build_merged_fundamental_metrics
from app.modules.indicators.pipeline import run_indicator_engine
from app.modules.stocks.repository import StockRepository


def _json_default_for_db(o: Any) -> Any:
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, (bytes, bytearray)):
        return o.decode("utf-8", errors="replace")
    if hasattr(o, "item") and callable(getattr(o, "item", None)):
        try:
            return o.item()
        except Exception:
            pass
    return str(o)


def _json_native_for_mysql(obj: Any) -> Any:
    """Round-trip sang kiểu JSON chuẩn của thư viện (tránh numpy / pymysql lỗi bind)."""
    return json.loads(json.dumps(obj, default=_json_default_for_db, ensure_ascii=False))


def _ai_text_field(v: Any) -> str | None:
    """Cột Text: PyMySQL không bind được dict — ép chuỗi nếu model trả object."""
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _ai_risks_for_db(v: Any) -> list[Any] | None:
    if v is None:
        return None
    if isinstance(v, list):
        out: list[Any] = []
        for item in v:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, (dict, list)):
                out.append(json.dumps(item, ensure_ascii=False))
            else:
                out.append(str(item))
        return out
    if isinstance(v, str):
        return [v]
    if isinstance(v, (dict, list)):
        return [json.dumps(v, ensure_ascii=False)]
    return [str(v)]


def _metric_float(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return float(v)


def _snapshot_indicator(v: Any) -> float | None:
    """Bỏ qua sentinel thiếu dữ liệu của engine (không ghi -9e6 vào DB)."""
    if v is None or is_missing_value(v):
        return None
    return float(v)


def _merge_fundamental_gaps(ai: dict[str, Any], ctx: dict[str, Any]) -> None:
    """Đảm bảo mọi khóa thiếu (server) có trong output để lưu DB / cải tiến prompt."""
    server_missing = [str(k) for k in (ctx.get("missing_numeric_keys") or [])]
    gaps = ai.get("fundamental_data_gaps")
    if not isinstance(gaps, list):
        gaps = []
    merged = sorted(set(server_missing) | {str(x) for x in gaps if x is not None})
    ai["fundamental_data_gaps"] = merged
    wish = ai.get("fundamental_wishlist")
    if not isinstance(wish, list):
        wish = []
    ai["fundamental_wishlist"] = [str(x) for x in wish if x is not None]


def _rule_based_recommendation(
    fundamental: int | None,
    technical: int,
    risk: int,
) -> str:
    """
    Khuyến nghị dự phòng / hiệu chỉnh (STOCK_ANALYSIS_STRATEGY §19 ví dụ BUY/WATCH/HOLD/AVOID).

    fundamental None → coi trung tính 50 để không lệch quá mức.
    risk_score của engine: càng cao càng rủi ro.
    """
    f = fundamental if fundamental is not None else 50
    if f >= 75 and technical >= 70 and risk <= 40:
        return "BUY"
    if risk >= 70 or (f < 40 and technical < 40):
        return "AVOID"
    if f >= 60 and technical < 55:
        return "WATCH"
    if technical >= 65 and f < 55:
        return "WATCH"
    if 40 <= technical <= 65 and 40 <= risk <= 60:
        return "HOLD"
    return "WATCH"


def _placeholder_ai(
    engine_payload: dict[str, Any],
    fundamental_ctx: dict[str, Any],
) -> dict[str, Any]:
    """Khi không gọi OpenAI hoặc lỗi API — vẫn trả JSON đủ field cho FE/DB."""
    st = engine_payload.get("state", {})
    sc = engine_payload.get("scores", {})
    missing = list(fundamental_ctx.get("missing_numeric_keys") or [])
    present = list(fundamental_ctx.get("present_numeric_keys") or [])
    has_m = bool(fundamental_ctx.get("has_key_metrics_row"))
    has_f = bool(fundamental_ctx.get("has_financial_report_row"))
    prof = fundamental_ctx.get("company_profile") or {}
    fm = engine_payload.get("fundamental_metrics") or {}
    if fm.get("status") == "unavailable":
        fa = "Không áp dụng do hệ thống không cung cấp dữ liệu cơ bản"
    elif present:
        fa = (
            f"Có {len(present)} chỉ số trong payload: {', '.join(present)}. "
            f"Chưa có giá trị cho: {', '.join(missing) if missing else '(không)'}. "
            "(OpenAI chưa bật/lỗi — chưa diễn giải sâu.)"
        )
    else:
        fa = (
            "Có bản ghi metrics hoặc BCTC nhưng các trường số chính đang trống; "
            "cần crawl/nhập liệu đầy đủ P/E, ROE, biên, tăng trưởng…"
        )
    wish = [
        "Đồng bộ đầy đủ stock_key_metrics (P/E, P/B, ROE, biên, tăng trưởng YoY, thanh khoản…)",
    ]
    if not has_f:
        wish.append("Bổ sung BCTC (stock_financial_reports) cho kỳ gần nhất")
    return {
        "summary": (
            f"Xu hướng: {st.get('primary_state', 'N/A')}. "
            f"Điểm xu hướng {sc.get('trend_score')}, động lượng {sc.get('momentum_score')}, "
            f"rủi ro {sc.get('risk_score')} (OpenAI chưa bật — bản tóm tắt rule-based)."
        ),
        "fundamental_analysis": fa,
        "technical_analysis": "Xem scores/state/strategies trong engine_output_json.",
        "risks": [
            "Thị trường có thể biến động bất thường",
            "Dữ liệu chỉ mang tính tham khảo, không phải tư vấn đầu tư",
        ],
        "conclusion": "Ưu tiên quản trị rủi ro và kịch bản vốn.",
        "recommendation": _rule_based_recommendation(
            engine_payload.get("fundamental_score"),
            int(engine_payload.get("technical_score", 50)),
            int(sc.get("risk_score", 50)),
        ),
        "fundamental_data_gaps": sorted(missing),
        "fundamental_wishlist": wish,
    }


class AnalysisHistoryService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._hist = AnalysisHistoryRepository(db)
        self._stocks = StockRepository(db)

    def run_analysis_for_ticker(self, user: User, ticker: str) -> dict[str, Any]:
        """
        Thực hiện các bước:
          1) Lấy cổ phiếu + chuỗi giá từ DB
          2) Chạy indicator engine (điểm, state, strategies, levels)
          3) Gắn fundamental_score + company + metrics cho payload AI
          4) Gọi OpenAI (nếu bật) hoặc placeholder
          5) Lưu analysis_requests + analysis_results (snapshot + engine_output_json + raw_ai)
        """
        stock = self._stocks.get_by_ticker(ticker)
        if not stock or not stock.is_active:
            raise StockNotFoundError()

        # Bước 1–2: dữ liệu giá → engine (đã có sẵn logic trong pipeline)
        bars = [
            self._stocks.price_row_to_bar(r)
            for r in self._stocks.get_price_rows_asc(stock.id, limit=400)
        ]
        engine = run_indicator_engine(bars, stock.ticker)

        # Bước 3: lớp cơ bản — gộp stock_key_metrics + BCTC (tỷ số, YoY) + P/E-P/B suy từ giá đóng
        metrics_row = self._stocks.get_latest_metrics(stock.id)
        db_metrics = self._stocks.metrics_to_dict(metrics_row) if metrics_row else None
        fin_rows = self._stocks.get_recent_financial_reports(stock.id, limit=2)
        fin_row = fin_rows[0] if fin_rows else None
        prev_fin_row = fin_rows[1] if len(fin_rows) > 1 else None
        fin_dict = self._stocks.financial_report_to_dict(fin_row) if fin_row else None
        prev_fin_dict = (
            self._stocks.financial_report_to_dict(prev_fin_row) if prev_fin_row else None
        )
        lp = engine.get("latest_price") or {}
        close_raw = lp.get("close")
        latest_close = float(close_raw) if close_raw is not None else None

        merged_metrics = build_merged_fundamental_metrics(
            db_metrics=db_metrics,
            latest_fin=fin_dict,
            previous_fin=prev_fin_dict,
            latest_close=latest_close,
        )
        fund_score = compute_fundamental_score(merged_metrics)
        engine["fundamental_score"] = fund_score
        engine["company"] = {
            "name": stock.company_name,
            "sector": stock.sector,
            "exchange": stock.exchange,
        }
        if merged_metrics:
            engine["fundamental_metrics"] = {**merged_metrics, "status": "available"}
        else:
            engine["fundamental_metrics"] = {"status": "unavailable"}
        engine["latest_financial_report"] = (
            fin_dict if fin_dict else {"status": "unavailable"}
        )

        fundamental_ctx = build_fundamental_context(
            ticker=stock.ticker,
            company_name=stock.company_name,
            exchange=stock.exchange,
            sector=stock.sector,
            description=stock.description,
            metrics_dict=merged_metrics,
            latest_financial_report=fin_dict,
            fundamental_score_0_100=fund_score,
            key_metrics_row_present=metrics_row is not None,
        )

        # Payload gửi AI: engine + bối cảnh cơ bản có cấu trúc (thiếu/đủ rõ ràng)
        ai_payload = {
            "engine": engine,
            "fundamental_context": fundamental_ctx,
            "instruction": (
                "Chỉ luận giải theo dữ liệu trong payload; không bịa số. "
                "Dùng fundamental_context (metrics, BCTC mới nhất nếu có, missing_numeric_keys)."
            ),
        }

        cfg = self._db.scalar(
            select(AiPromptConfig).where(
                AiPromptConfig.name == "stock_analysis_v1",
                AiPromptConfig.is_active.is_(True),
            )
        )
        system_prompt = (cfg.system_prompt if cfg else None) or DEFAULT_SYSTEM_PROMPT
        user_template = cfg.user_prompt_template if cfg else None

        # Bước 4: AI — lỗi mạng/format → fallback placeholder (FE không crash)
        if settings.openai_enabled:
            user_msg = build_user_message(ai_payload, user_template)
            try:
                ai_parsed = call_openai_analysis(system_prompt, user_msg)
            except Exception:
                ai_parsed = _placeholder_ai(engine, fundamental_ctx)
        else:
            ai_parsed = _placeholder_ai(engine, fundamental_ctx)

        _merge_fundamental_gaps(ai_parsed, fundamental_ctx)

        rule_rec = _rule_based_recommendation(
            fund_score,
            engine["technical_score"],
            engine["scores"]["risk_score"],
        )
        if ai_parsed.get("recommendation") in (None, "", "null"):
            ai_parsed["recommendation"] = rule_rec

        # Bước 5: ghi DB — giữ request để truy vết; result chứa snapshot + JSON đầy đủ
        req = self._hist.create_request(
            user_id=user.id,
            stock_id=stock.id,
            request_type="full",
            status="processing",
        )
        analysis_date = date.fromisoformat(engine["analysis_date"])
        lp = engine["latest_price"]
        ind = engine["indicators"]
        result = self._hist.create_result(
            analysis_request_id=req.id,
            user_id=user.id,
            stock_id=stock.id,
            analysis_date=analysis_date,
            snapshot_price=lp.get("close"),
            snapshot_volume=lp.get("volume"),
            snapshot_pe=_metric_float(merged_metrics.get("pe")) if merged_metrics else None,
            snapshot_pb=_metric_float(merged_metrics.get("pb")) if merged_metrics else None,
            snapshot_roe=_metric_float(merged_metrics.get("roe")) if merged_metrics else None,
            snapshot_rsi=_snapshot_indicator(ind.get("rsi_14")),
            snapshot_macd=_snapshot_indicator(ind.get("macd")),
            fundamental_score=fund_score,
            technical_score=engine["technical_score"],
            risk_score=engine["scores"]["risk_score"],
            ai_summary=_ai_text_field(ai_parsed.get("summary")),
            ai_fundamental_analysis=_ai_text_field(ai_parsed.get("fundamental_analysis")),
            ai_technical_analysis=_ai_text_field(ai_parsed.get("technical_analysis")),
            ai_risks_json=_ai_risks_for_db(ai_parsed.get("risks")),
            ai_conclusion=_ai_text_field(ai_parsed.get("conclusion")),
            ai_recommendation=str(ai_parsed.get("recommendation", rule_rec))[:32],
            raw_ai_response_json=_json_native_for_mysql(ai_parsed),
            engine_output_json=_json_native_for_mysql(engine),
        )
        self._hist.update_request_status(req, "completed")

        return {
            "result_id": result.id,
            "engine": engine,
            "ai": ai_parsed,
        }
