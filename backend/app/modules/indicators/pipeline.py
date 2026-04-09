"""
Pipeline tổng hợp engine phân tích kỹ thuật (theo stock_analysis_strategy_engine.md).

Luồng chuẩn:
    OHLCV → chuẩn hóa & feature → scoring → phân loại trạng thái thị trường
    → strategy engine → mức hỗ trợ/kháng cự & lớp rủi ro → JSON API.

Nguyên tắc: AI chỉ luận giải trên output đã tính; không thay thế các bước này.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd

from app.core.exceptions import AppError
from app.modules.indicators.data_processing import bars_to_dataframe
from app.modules.indicators.features import enrich_features
from app.modules.indicators.market_state import classify_market_state
from app.modules.indicators.scores import attach_drawdown_proxy, compute_all_scores
from app.modules.indicators.strategies_engine import (
    build_levels,
    build_risk_layer,
    run_strategies,
)

# SMA200 cần ít nhất 200 phiên; thêm đệm để slope/volume ổn định (tài liệu engine).
MIN_BARS = 200


def run_indicator_engine(price_bars: list[dict[str, Any]], symbol: str) -> dict[str, Any]:
    """
    Chạy full engine trên chuỗi giá đã sắp xếp theo thời gian (phiên cuối = mới nhất).

    Trả về cấu trúc gần với mục §33 engine doc (symbol, scores, state, strategies, …).
    """
    if len(price_bars) < MIN_BARS:
        raise AppError(
            f"Cần tối thiểu {MIN_BARS} phiên giá để tính đầy đủ engine (SMA200, v.v.)",
            "INSUFFICIENT_PRICE_HISTORY",
        )

    # 1) Chuẩn hóa OHLCV, kiểm tra tính hợp lệ nến/volume
    base = bars_to_dataframe(price_bars)

    # 2) Feature engineering: MA, momentum, volume, biến động, cấu trúc giá
    feat = enrich_features(base)

    # 3) Drawdown nội bộ (proxy) phục vụ risk_score — max drawdown từ đỉnh lũy kế
    feat = attach_drawdown_proxy(feat)

    last = feat.iloc[-1]

    # 4) Chấm điểm 0–100 từng khía cạnh (§13–19 engine doc)
    scores = compute_all_scores(last)

    # 5) Một trạng thái thị trường chính (§20–21)
    state = classify_market_state(last, scores)

    # 6) Chiến lược đang “active” theo state + điều kiện giá (§22–27)
    strategies = run_strategies(last, scores, state["primary_state"])

    # 7) Hỗ trợ/kháng cự gần (§30)
    levels = build_levels(last)

    # 8) Gói quản trị rủi ro tóm tắt (§31)
    risk = build_risk_layer(scores, levels)

    # Ngày phân tích: ưu tiên ngày của nến cuối, fallback hôm nay
    analysis_date = date.today()
    if "date" in last.index and pd.notna(last["date"]):
        d = last["date"]
        analysis_date = d if isinstance(d, date) else pd.to_datetime(d).date()

    latest_price = {
        "open": float(last["open"]),
        "high": float(last["high"]),
        "low": float(last["low"]),
        "close": float(last["close"]),
        "volume": int(last["volume"]),
        "change": float(last["price_change"]) if pd.notna(last.get("price_change")) else None,
        "change_pct": float(last["price_change_pct"])
        if pd.notna(last.get("price_change_pct"))
        else None,
    }

    def nz(x: Any) -> float | None:
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return None
        return float(x)

    # Tập chỉ báo trả API/AI — subset rõ ràng (tránh dump toàn bộ cột nội bộ)
    indicators = {
        "sma_20": nz(last.get("sma_20")),
        "sma_50": nz(last.get("sma_50")),
        "sma_200": nz(last.get("sma_200")),
        "ema_12": nz(last.get("ema_12")),
        "ema_26": nz(last.get("ema_26")),
        "rsi_14": nz(last.get("rsi_14")),
        "macd": nz(last.get("macd")),
        "macd_signal": nz(last.get("macd_signal")),
        "macd_histogram": nz(last.get("macd_histogram")),
        "atr_14": nz(last.get("atr_14")),
        "volume_ratio": nz(last.get("volume_ratio")),
        "bollinger_width": nz(last.get("bollinger_width")),
    }

    # technical_score tổng hợp cho DB và rule khuyến nghị (STOCK_ANALYSIS_STRATEGY):
    # trung bình xu hướng + động lượng + thanh khoản + breakout (bỏ volatility_score
    # vì vai trò khác — đo “phù hợp biến động”, không phải xu hướng thuần).
    technical_score = int(
        round(
            (
                scores["trend_score"]
                + scores["momentum_score"]
                + scores["volume_score"]
                + scores["breakout_score"]
            )
            / 4
        )
    )

    return {
        "symbol": symbol,
        "analysis_date": analysis_date.isoformat(),
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "latest_price": latest_price,
        "indicators": indicators,
        "scores": scores,
        "state": state,
        "levels": levels,
        "active_strategies": strategies,
        "risk": risk,
        "technical_score": technical_score,
    }
