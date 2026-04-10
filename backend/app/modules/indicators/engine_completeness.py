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


def compute_computed_bias(trend_score: int) -> str:
    if trend_score >= 60:
        return "bullish"
    if trend_score <= 40:
        return "bearish"
    return "neutral"


def calculate_confidence(scores: dict[str, int], indicators: dict[str, float]) -> int:
    """
    0–100: đồng thuận giữa các score kỹ thuật, trừ rủi ro và bất đồng trend/momentum;
    cộng nhẹ khi nhiều chỉ báo có giá trị hợp lệ trong snapshot.
    """
    t = int(scores.get("trend_score", 50))
    m = int(scores.get("momentum_score", 50))
    v = int(scores.get("volume_score", 50))
    b = int(scores.get("breakout_score", 50))
    r = int(scores.get("risk_score", 50))

    core = (t + m + v + b) / 4.0
    disagreement_penalty = min(28, abs(t - m) * 0.28)
    risk_penalty = max(0, r - 42) * 0.22
    present = sum(1 for x in indicators.values() if not is_missing_value(x))
    data_boost = min(12, present)

    raw = core - disagreement_penalty - risk_penalty + data_boost
    return int(max(0, min(100, round(raw))))


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
    if ts >= 60:
        trend_s = f"{base_t} → Xu hướng nghiêng tích cực theo engine."
    elif ts <= 40:
        trend_s = f"{base_t} → Xu hướng nghiêng tiêu cực theo engine."
    else:
        trend_s = f"{base_t} → Xu hướng trung tính (khoảng 41–59) theo engine."

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
