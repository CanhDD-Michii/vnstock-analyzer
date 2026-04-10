"""
Scoring Engine (engine doc §13–19).

Mỗi điểm 0–100, cộng điểm theo checklist gợi ý trong tài liệu rồi clip.
Lưu ý:
  - risk_score: điểm CÀNG CAO = rủi ro CÀNG CAO (không phải “điểm an toàn”).
  - volatility_score: điểm cao khi biến động “vừa phải”, quá thấp/quá hỗn loạn bị trừ (§17).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from app.modules.indicators.features import last_numeric


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return float(max(lo, min(hi, x)))


def compute_trend_score(row: pd.Series) -> int:
    """
    Trend score — §14 engine doc.
    Thưởng khi giá trên MA, MA xếp chồng bull, slope dương, gần đỉnh 20 phiên.
    """
    score = 0.0
    c = last_numeric(row, "close")
    sma20 = last_numeric(row, "sma_20")
    sma50 = last_numeric(row, "sma_50")
    sma200 = last_numeric(row, "sma_200")
    hh20 = last_numeric(row, "highest_high_20")

    if c > sma20 > 0:
        score += 15
    if c > sma50 > 0:
        score += 10
    if sma20 > sma50 > 0:
        score += 20
    if sma50 > sma200 > 0:
        score += 15
    if last_numeric(row, "trend_slope_20") > 0:
        score += 15
    if last_numeric(row, "trend_slope_50") > 0:
        score += 10
    # Gần đỉnh 20 phiên (không bắt buộc đã breakout)
    if hh20 > 0 and c >= hh20 * 0.98:
        score += 15
    return int(_clip(score))


def compute_momentum_score(row: pd.Series) -> int:
    """
    Momentum score — §15.
    RSI, MACD, histogram, ROC, Stoch, vị trí close trong range phiên.
    """
    score = 0.0
    rsi = last_numeric(row, "rsi_14")
    macd = last_numeric(row, "macd")
    sig = last_numeric(row, "macd_signal")
    hist = last_numeric(row, "macd_histogram")
    roc = last_numeric(row, "roc_10")
    st_k = last_numeric(row, "stoch_k")
    st_d = last_numeric(row, "stoch_d")
    cpos = last_numeric(row, "close_position_in_range")

    if rsi > 55:
        score += 20
    if rsi > 60:
        score += 10
    if macd > sig:
        score += 20
    if hist > 0:
        score += 15
    if roc > 0:
        score += 15
    if st_k > st_d:
        score += 10
    if cpos > 0.65:
        score += 10
    return int(_clip(score))


def compute_volume_score(row: pd.Series) -> int:
    """
    Volume score — §16.
    Nền theo volume_ratio (luôn trong [30, 100], không bao giờ 0); cộng thưởng xác nhận.
    """
    vr = last_numeric(row, "volume_ratio")
    if math.isnan(vr) or vr <= 0:
        base = 50.0
    elif vr < 0.5:
        base = 30.0
    elif vr < 1.0:
        base = 50.0
    else:
        base = 70.0

    bonus = 0.0
    daily_ret = last_numeric(row, "daily_return")
    vol = last_numeric(row, "volume")
    vol_ma = last_numeric(row, "volume_sma_20")

    if vr > 1.2:
        bonus += 15
    if vr > 1.5:
        bonus += 10
    if daily_ret > 0 and vol_ma > 0 and vol > vol_ma:
        bonus += 15
    vt = row.get("volume_trend")
    if vt is not None and not (isinstance(vt, float) and math.isnan(vt)) and float(vt) > 0:
        bonus += 10
    c = last_numeric(row, "close")
    hh20 = last_numeric(row, "highest_high_20")
    if hh20 > 0 and c >= hh20 and vr > 1.2:
        bonus += 10

    return int(_clip(base + bonus, 30.0, 100.0))


def compute_volatility_score(row: pd.Series) -> int:
    """
    Volatility score — §17.
    Heuristic: ATR/close và Bollinger width nằm trong vùng “vừa phải” được thưởng;
    quá trầm hoặc quá nóng bị phạt (không dùng if-else cứng theo từng mã).
    """
    atr = last_numeric(row, "atr_14")
    c = last_numeric(row, "close")
    bw = last_numeric(row, "bollinger_width")
    rel_atr = (atr / c) if c > 0 else 0.0
    score = 50.0
    if 0.01 <= rel_atr <= 0.04:
        score += 25
    elif rel_atr < 0.01:
        score += 5
    else:
        score -= min(30, (rel_atr - 0.04) * 500)
    if 0.02 <= bw <= 0.12:
        score += 15
    elif bw < 0.02:
        score += 5
    else:
        score -= min(20, (bw - 0.12) * 100)
    return int(_clip(score))


def compute_risk_score(row: pd.Series) -> int:
    """
    Risk score — §18.
    Điểm tăng khi: dưới MA, MACD yếu, RSI thấp, phân phối volume khi giảm,
    sát hỗ trợ, drawdown proxy lớn.
    """
    score = 0.0
    c = last_numeric(row, "close")
    sma20 = last_numeric(row, "sma_20")
    sma50 = last_numeric(row, "sma_50")
    rsi = last_numeric(row, "rsi_14")
    macd = last_numeric(row, "macd")
    sig = last_numeric(row, "macd_signal")
    vr = last_numeric(row, "volume_ratio")
    dist_sup = last_numeric(row, "distance_to_support")

    if c < sma20 > 0:
        score += 15
    if c < sma50 > 0:
        score += 15
    if macd < sig:
        score += 10
    if rsi < 45:
        score += 10
    daily_ret = last_numeric(row, "daily_return")
    if daily_ret < 0 and vr > 1.3:
        score += 15
    if dist_sup < 0.01:
        score += 15
    dd = row.get("drawdown_proxy")
    if dd is not None and not (isinstance(dd, float) and np.isnan(dd)) and float(dd) > 0.2:
        score += 15
    return int(_clip(score))


def compute_breakout_score(row: pd.Series) -> int:
    """Breakout score — §19. Giá vượt đỉnh 20 phiên, volume, squeeze Bollinger, RSI, vị trí nến."""
    score = 0.0
    c = last_numeric(row, "close")
    hh20 = last_numeric(row, "highest_high_20")
    vr = last_numeric(row, "volume_ratio")
    bw = last_numeric(row, "bollinger_width")
    rsi = last_numeric(row, "rsi_14")
    cpos = last_numeric(row, "close_position_in_range")
    dist_sup = last_numeric(row, "distance_to_support")

    if hh20 > 0 and c >= hh20:
        score += 25
    if vr > 1.5:
        score += 25
    if bw < 0.04:
        score += 15
    if rsi > 60:
        score += 10
    if cpos > 0.7:
        score += 10
    if dist_sup > 0.02:
        score += 15
    return int(_clip(score))


def attach_drawdown_proxy(feat: pd.DataFrame) -> pd.DataFrame:
    """
    Drawdown so với đỉnh lũy kế từ đầu chuỗi — proxy rủi ro (không thay thế max DD 52 tuần đầy đủ).
    """
    out = feat.copy()
    c = out["close"]
    rolling_max = c.cummax()
    out["drawdown_proxy"] = np.where(rolling_max > 0, (rolling_max - c) / rolling_max, 0.0)
    return out


def compute_all_scores(last_row: pd.Series) -> dict[str, int]:
    """Gói 6 score cho phiên cuối cùng."""
    return {
        "trend_score": compute_trend_score(last_row),
        "momentum_score": compute_momentum_score(last_row),
        "volume_score": compute_volume_score(last_row),
        "volatility_score": compute_volatility_score(last_row),
        "risk_score": compute_risk_score(last_row),
        "breakout_score": compute_breakout_score(last_row),
    }
