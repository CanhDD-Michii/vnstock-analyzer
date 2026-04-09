"""
Luồng phân tích end-to-end khi user gọi POST /analysis/{ticker}
(STOCK_ANALYSIS_STRATEGY §42 — Data → chỉ số → score → OpenAI → lưu DB).

Nguyên tắc CODE_RULES: orchestration ở service; engine thuần tính toán ở modules.indicators;
AI chỉ luận giải trên payload đã có, không bịa số.
"""

from __future__ import annotations

from datetime import date
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
from app.modules.indicators.fundamental import compute_fundamental_score
from app.modules.indicators.pipeline import run_indicator_engine
from app.modules.stocks.repository import StockRepository


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


def _placeholder_ai(engine_payload: dict[str, Any]) -> dict[str, Any]:
    """Khi không gọi OpenAI hoặc lỗi API — vẫn trả JSON đủ field cho FE/DB."""
    st = engine_payload.get("state", {})
    sc = engine_payload.get("scores", {})
    return {
        "summary": (
            f"Xu hướng: {st.get('primary_state', 'N/A')}. "
            f"Điểm xu hướng {sc.get('trend_score')}, động lượng {sc.get('momentum_score')}, "
            f"rủi ro {sc.get('risk_score')} (OpenAI chưa bật — bản tóm tắt rule-based)."
        ),
        "fundamental_analysis": "Chưa gọi OpenAI hoặc chưa có dữ liệu cơ bản chi tiết trong payload.",
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

        # Bước 3: lớp cơ bản (có thể rỗng)
        metrics_row = self._stocks.get_latest_metrics(stock.id)
        metrics_dict = self._stocks.metrics_to_dict(metrics_row) if metrics_row else None
        fund_score = compute_fundamental_score(metrics_dict)
        engine["fundamental_score"] = fund_score
        engine["company"] = {
            "name": stock.company_name,
            "sector": stock.sector,
            "exchange": stock.exchange,
        }
        engine["fundamental_metrics"] = metrics_dict

        # Payload gửi AI: chỉ dữ liệu đã tính (engine doc §32 — không tự bịa)
        ai_payload = {
            "engine": engine,
            "instruction": "Chỉ luận giải theo engine; không bịa số.",
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
                ai_parsed = _placeholder_ai(engine)
        else:
            ai_parsed = _placeholder_ai(engine)

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
            snapshot_pe=metrics_dict.get("pe") if metrics_dict else None,
            snapshot_pb=metrics_dict.get("pb") if metrics_dict else None,
            snapshot_roe=metrics_dict.get("roe") if metrics_dict else None,
            snapshot_rsi=ind.get("rsi_14"),
            snapshot_macd=ind.get("macd"),
            fundamental_score=fund_score,
            technical_score=engine["technical_score"],
            risk_score=engine["scores"]["risk_score"],
            ai_summary=ai_parsed.get("summary"),
            ai_fundamental_analysis=ai_parsed.get("fundamental_analysis"),
            ai_technical_analysis=ai_parsed.get("technical_analysis"),
            ai_risks_json=ai_parsed.get("risks"),
            ai_conclusion=ai_parsed.get("conclusion"),
            ai_recommendation=str(ai_parsed.get("recommendation", rule_rec))[:32],
            raw_ai_response_json=ai_parsed,
            engine_output_json=engine,
        )
        self._hist.update_request_status(req, "completed")

        return {
            "result_id": result.id,
            "engine": engine,
            "ai": ai_parsed,
        }
