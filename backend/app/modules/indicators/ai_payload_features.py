"""
Gói chỉ số / feature đã tính sẵn, chuẩn hóa cho lớp AI (bổ sung cho indicators thô).

- Tỷ lệ & khoảng cách: đưa về % so với giá / MA để model đọc nhanh.
- Phân vùng (RSI zone, MA alignment, MACD vs signal): nhãn rời rạc từ cùng dữ liệu engine.
- Không thay thế scores/state — chỉ làm rõ ngữ cảnh số học.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.modules.indicators.features import last_numeric


def _nz_float(x: Any, digits: int | None = 4) -> float | None:
    if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if np.isnan(v) or np.isinf(v):
        return None
    return round(v, digits) if digits is not None else v


def _pct_from_ratio(ratio: float | None, digits: int = 3) -> float | None:
    if ratio is None:
        return None
    return _nz_float(float(ratio) * 100.0, digits)


def _rsi_zone(rsi: float | None) -> str | None:
    if rsi is None:
        return None
    r = float(rsi)
    if r < 30:
        return "oversold"
    if r < 45:
        return "weak_bearish"
    if r < 55:
        return "neutral"
    if r < 70:
        return "strong_bullish"
    return "overbought"


def _ma_alignment(row: pd.Series) -> str | None:
    s20, s50, s200 = last_numeric(row, "sma_20"), last_numeric(row, "sma_50"), last_numeric(row, "sma_200")
    if s20 <= 0 or s50 <= 0 or s200 <= 0:
        return None
    if s20 > s50 > s200:
        return "bull_stack"
    if s20 < s50 < s200:
        return "bear_stack"
    return "mixed"


def _macd_cross_hint(last: pd.Series, prev: pd.Series | None) -> str | None:
    if prev is None:
        return None
    m0, s0 = last_numeric(last, "macd"), last_numeric(last, "macd_signal")
    m1, s1 = last_numeric(prev, "macd"), last_numeric(prev, "macd_signal")
    if m0 > s0 and m1 <= s1:
        return "bullish_cross"
    if m0 < s0 and m1 >= s1:
        return "bearish_cross"
    return None


def _as_bool_opt(val: Any) -> bool | None:
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        return None
    return bool(val)


def _bollinger_position(row: pd.Series) -> float | None:
    c = last_numeric(row, "close")
    lo = last_numeric(row, "bollinger_lower")
    hi = last_numeric(row, "bollinger_upper")
    if hi <= lo or c <= 0:
        return None
    pos = (c - lo) / (hi - lo)
    if np.isnan(pos):
        return None
    return _nz_float(pos, 4)


def build_normalized_features_for_ai(
    last: pd.Series,
    prev: pd.Series | None = None,
) -> dict[str, Any]:
    """
    Snapshot phiên cuối: chỉ số tương đối / nhãn, đồng bộ công thức features.py & scores.py.
    """
    c = last_numeric(last, "close")
    rsi = last.get("rsi_14")
    rsi_f = None if rsi is None or (isinstance(rsi, float) and np.isnan(rsi)) else float(rsi)

    rel_atr = (last_numeric(last, "atr_14") / c) if c > 0 else None

    macd = last_numeric(last, "macd")
    sig = last_numeric(last, "macd_signal")
    macd_state = "macd_above_signal" if macd > sig else "macd_below_signal" if macd < sig else "macd_equals_signal"

    price_action = {
        "daily_return_pct": _pct_from_ratio(last.get("daily_return")),
        "gap_pct": _pct_from_ratio(last.get("gap_percent")),
        "close_position_in_bar_0_to_1": _nz_float(last.get("close_position_in_range")),
        "intraday_range_pct": _pct_from_ratio(last.get("intraday_range")),
    }

    trend = {
        "close_above_sma20": _as_bool_opt(last.get("close_above_sma20")),
        "close_above_sma50": _as_bool_opt(last.get("close_above_sma50")),
        "close_above_sma200": _as_bool_opt(last.get("close_above_sma200")),
        "sma20_above_sma50": _as_bool_opt(last.get("sma20_above_sma50")),
        "sma50_above_sma200": _as_bool_opt(last.get("sma50_above_sma200")),
        "ma_alignment": _ma_alignment(last),
        "distance_close_to_sma20_pct": _pct_from_ratio(last.get("distance_to_sma20")),
        "distance_close_to_sma50_pct": _pct_from_ratio(last.get("distance_to_sma50")),
        "distance_close_to_sma200_pct": _pct_from_ratio(last.get("distance_to_sma200")),
        "sma20_slope_5d_pct": _pct_from_ratio(last.get("trend_slope_20")),
        "sma50_slope_5d_pct": _pct_from_ratio(last.get("trend_slope_50")),
    }

    momentum = {
        "rsi_14": _nz_float(rsi_f, 2),
        "rsi_zone": _rsi_zone(rsi_f),
        "macd_vs_signal_state": macd_state,
        "macd_signal_cross_hint": _macd_cross_hint(last, prev),
        "stoch_k": _nz_float(last.get("stoch_k"), 2),
        "stoch_d": _nz_float(last.get("stoch_d"), 2),
        "roc_10_pct": _nz_float(last.get("roc_10"), 3),
    }

    vol = {
        "atr_pct_of_close": _pct_from_ratio(rel_atr),
        "bollinger_width_ratio": _nz_float(last.get("bollinger_width")),
        "bollinger_close_position_0_to_1": _bollinger_position(last),
        "rolling_std_20_daily_return_stdev_pct": _pct_from_ratio(last.get("rolling_std_20")),
    }

    volume_block = {
        "volume_ratio_vs_20d_sma": _nz_float(last.get("volume_ratio"), 3),
        "volume_trend_5v20": _nz_float(last.get("volume_trend"), 2),
    }

    structure = {
        "distance_to_20d_high_pct": _pct_from_ratio(last.get("distance_to_breakout")),
        "distance_above_20d_low_pct": _pct_from_ratio(last.get("distance_to_support")),
        "drawdown_from_series_peak_pct": _pct_from_ratio(last.get("drawdown_proxy")),
    }

    return {
        "as_of": "latest_bar_in_series",
        "price_action": price_action,
        "trend_structure": trend,
        "momentum": momentum,
        "volatility": vol,
        "volume": volume_block,
        "structure_and_risk_proxies": structure,
    }
