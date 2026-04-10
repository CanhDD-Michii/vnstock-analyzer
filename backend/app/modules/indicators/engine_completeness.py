"""
Bổ sung độ đầy đủ payload engine: confidence, bias, signal_summary, sentinel số thay null.

- MISSING_INDICATOR_VALUE (-1.0): chỉ báo không tính được trong snapshot (tránh JSON null).
"""

from __future__ import annotations

import math
from typing import Any

# Giá trị không thể trùng MACD/giá thực tế — thay thế null trong JSON
MISSING_INDICATOR_VALUE = -9_999_999.0


def is_missing_value(x: Any) -> bool:
    try:
        f = float(x)
    except (TypeError, ValueError):
        return True
    if math.isnan(f):
        return True
    return f <= MISSING_INDICATOR_VALUE + 1.0


def sanitize_indicator_map(raw: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k, v in raw.items():
        if v is None:
            out[k] = MISSING_INDICATOR_VALUE
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            out[k] = MISSING_INDICATOR_VALUE
            continue
        if math.isnan(f):
            out[k] = MISSING_INDICATOR_VALUE
        else:
            out[k] = f
    return out


def sanitize_levels_map(levels: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k, v in levels.items():
        if v is None:
            out[k] = MISSING_INDICATOR_VALUE
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            out[k] = MISSING_INDICATOR_VALUE
            continue
        if math.isnan(f):
            out[k] = MISSING_INDICATOR_VALUE
        else:
            out[k] = f
    return out


def sanitize_risk_map(risk: dict[str, Any]) -> dict[str, Any]:
    out = dict(risk)
    for key in ("stop_watch_zone", "invalidation_zone"):
        v = out.get(key)
        if v is None:
            out[key] = MISSING_INDICATOR_VALUE
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            out[key] = MISSING_INDICATOR_VALUE
            continue
        if math.isnan(f):
            out[key] = MISSING_INDICATOR_VALUE
        else:
            out[key] = f
    return out


def sanitize_latest_price_map(lp: dict[str, Any]) -> dict[str, Any]:
    out = dict(lp)
    for key in ("change", "change_pct"):
        v = out.get(key)
        if v is None:
            out[key] = 0.0
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            out[key] = 0.0
            continue
        if math.isnan(f):
            out[key] = 0.0
        else:
            out[key] = f
    return out


def normalized_features_without_null(obj: Any) -> Any:
    """Thay None trong cây dict/list bằng 'unavailable' để JSON không chứa null."""
    if obj is None:
        return "unavailable"
    if isinstance(obj, dict):
        return {k: normalized_features_without_null(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalized_features_without_null(v) for v in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return "unavailable"
    return obj


def compute_computed_bias(trend_score: int, indicators: dict[str, float]) -> str:
    """
    Xu hướng theo trend_score (55/45); MACD vs signal + RSI gán weak_bullish / weak_bearish
    khi không đã bullish/bearish “đủ mạnh” từ trend.
    """
    ts = int(trend_score)
    if ts >= 55:
        bias = "bullish"
    elif ts <= 45:
        bias = "bearish"
    else:
        bias = "neutral"

    macd = indicators.get("macd")
    sig = indicators.get("macd_signal")
    rsi = indicators.get("rsi_14")
    if is_missing_value(macd) or is_missing_value(sig) or is_missing_value(rsi):
        return bias

    macd_f = float(macd)
    sig_f = float(sig)
    rsi_f = float(rsi)

    if macd_f > sig_f and rsi_f > 50:
        if bias == "bullish":
            return "bullish"
        return "weak_bullish"
    if macd_f < sig_f and rsi_f < 50:
        if bias == "bearish":
            return "bearish"
        return "weak_bearish"
    return bias


def calculate_confidence(scores: dict[str, int], indicators: dict[str, float]) -> int:
    """
    0–100: trung bình có trọng số trend / momentum / volume / breakout;
    volume tối đa 30% — một metric không “kill” toàn bộ tín hiệu.
    (Tham số indicators giữ chữ ký API; có thể dùng sau cho boost độ đầy đủ snapshot.)
    """
    t = float(int(scores.get("trend_score", 50)))
    m = float(int(scores.get("momentum_score", 50)))
    v = float(int(scores.get("volume_score", 50)))
    br = float(int(scores.get("breakout_score", 50)))
    conf = 0.25 * t + 0.25 * m + 0.30 * v + 0.20 * br
    return int(max(0, min(100, round(conf))))


def build_signal_summary(
    scores: dict[str, int],
    indicators: dict[str, float],
    primary_state: str,
    overall_bias: str,
) -> dict[str, str]:
    ts = int(scores.get("trend_score", 50))
    ms = int(scores.get("momentum_score", 50))
    vs = int(scores.get("volume_score", 50))
    rsi = float(indicators.get("rsi_14", MISSING_INDICATOR_VALUE))
    vr = float(indicators.get("volume_ratio", MISSING_INDICATOR_VALUE))
    macd = float(indicators.get("macd", MISSING_INDICATOR_VALUE))
    sig = float(indicators.get("macd_signal", MISSING_INDICATOR_VALUE))

    base_t = f"trend_score={ts}/100, state={primary_state}"
    if ts >= 55:
        trend_s = f"{base_t} → Xu hướng nghiêng tích cực theo engine."
    elif ts <= 45:
        trend_s = f"{base_t} → Xu hướng nghiêng tiêu cực theo engine."
    else:
        trend_s = f"{base_t} → Xu hướng trung tính (khoảng 46–54) theo engine."

    mom_bits = [f"momentum_score={ms}/100"]
    if not is_missing_value(rsi):
        mom_bits.append(f"RSI_14={rsi:.2f}")
    if not is_missing_value(macd) and not is_missing_value(sig):
        mom_bits.append("MACD>signal" if macd > sig else "MACD<signal" if macd < sig else "MACD=signal")
    elif is_missing_value(macd) or is_missing_value(sig):
        mom_bits.append("MACD/signal không đủ snapshot")
    mom_qual = "mạnh" if ms >= 60 else "yếu" if ms <= 40 else "trung bình"
    momentum_s = ", ".join(mom_bits) + f" → Động lượng {mom_qual} theo điểm engine."

    vol_bits = [f"volume_score={vs}/100"]
    if not is_missing_value(vr):
        vol_bits.append(f"volume_ratio={vr:.2f}")
    else:
        vol_bits.append("volume_ratio=không đủ snapshot")
    if vs >= 60 and not is_missing_value(vr) and vr >= 1.0:
        vol_qual = "cao / xác nhận tương đối tốt"
    elif vs <= 40 or (not is_missing_value(vr) and vr < 0.85):
        vol_qual = "thấp / thiếu xác nhận"
    else:
        vol_qual = "trung bình"
    volume_s = ", ".join(vol_bits) + f" → Thanh khoản {vol_qual} (theo payload)."

    return {
        "trend": trend_s,
        "momentum": momentum_s,
        "volume": volume_s,
        "overall_bias": overall_bias,
    }
