"""
Strategy Engine + Support/Resistance + Risk layer (engine doc §22–31).

- run_strategies: theo state, gắn 1+ chiến lược (Trend Following, Pullback, Breakout, …).
- build_levels: hỗ trợ/kháng cự từ đỉnh/đáy cửa sổ 20–50 phiên (proxy §30).
- build_risk_layer: gói risk_level + vùng theo dõi (§31).
"""

from __future__ import annotations

import pandas as pd

from app.modules.indicators.features import last_numeric


def _avg_confidence(scores: dict[str, int], keys: list[str]) -> int:
    """Độ tin cậy chiến lược: trung bình các score liên quan (0–100)."""
    vals = [scores[k] for k in keys if k in scores]
    return int(sum(vals) / len(vals)) if vals else 50


def run_strategies(
    last_row: pd.Series,
    scores: dict[str, int],
    state: str,
) -> list[dict]:
    """
    Sinh danh sách chiến lược “đang active” + signal + confidence + reason + risk_notes.
    Khớp tinh thần §23–27 (không hard-code lệnh mua/bán tuyệt đối).
    """
    strategies: list[dict] = []
    c = last_numeric(last_row, "close")
    sma20 = last_numeric(last_row, "sma_20")
    sma50 = last_numeric(last_row, "sma_50")
    rsi = last_numeric(last_row, "rsi_14")
    macd = last_numeric(last_row, "macd")
    sig = last_numeric(last_row, "macd_signal")
    vr = last_numeric(last_row, "volume_ratio")
    hh20 = last_numeric(last_row, "highest_high_20")
    dist20 = last_numeric(last_row, "distance_to_sma20")

    # STRATEGY_1 + STRATEGY_2 — Trend / Pullback (§23–24)
    if state in ("Strong Uptrend", "Weak Uptrend"):
        conf = _avg_confidence(scores, ["trend_score", "momentum_score", "volume_score"])
        sig_txt = "Strong Positive" if state == "Strong Uptrend" else "Positive"
        strategies.append(
            {
                "name": "Trend Following",
                "signal": sig_txt,
                "confidence": conf,
                "reason": "Giá duy trì trên MA20/MA50, MACD và RSI hỗ trợ xu hướng hiện tại.",
                "risk_notes": [
                    "Nếu mất MA20, độ mạnh xu hướng suy giảm",
                    "Tránh mua đuổi khi RSI quá nóng",
                ],
            }
        )
        # Pullback: giá trên SMA50, gần MA20, RSI chưa quá nóng, volume không bùng khi chỉnh
        pullback_ok = (
            c > sma50 > 0
            and abs(dist20) < 0.03
            and rsi < 60
            and vr < 1.3
        )
        if pullback_ok:
            strategies.append(
                {
                    "name": "Pullback Buy",
                    "signal": "Watch",
                    "confidence": min(85, conf - 5),
                    "reason": "Giá điều chỉnh về vùng gần MA20 trong xu hướng tăng, volume co nhẹ.",
                    "risk_notes": [
                        "Pullback sâu thủng MA50 là tín hiệu xấu",
                        "Cần volume không bùng nổ bên bán",
                    ],
                }
            )

    # STRATEGY_3 — Breakout (§25)
    if state in ("Sideway Accumulation", "Breakout Setup"):
        brk_conf = scores.get("breakout_score", 50)
        sig_b = "Breakout Confirmed" if c >= hh20 > 0 and vr > 1.5 else "Watch Closely"
        strategies.append(
            {
                "name": "Breakout Detection",
                "signal": sig_b,
                "confidence": brk_conf,
                "reason": "Giá tiến gần kháng cự 20 phiên, biên độ Bollinger và volume được theo dõi.",
                "risk_notes": [
                    "Breakout yếu nếu đóng cửa không giữ được gần đỉnh phiên",
                    "False breakout nếu volume không xác nhận",
                ],
            }
        )

    # STRATEGY_4 — Mean reversion / oversold bounce (§26)
    if state == "Oversold Rebound Candidate":
        strategies.append(
            {
                "name": "Mean Reversion / Oversold Bounce",
                "signal": "Watch",
                "confidence": min(70, scores.get("momentum_score", 40) + 10),
                "reason": "RSI thấp và có dấu hiệu hồi kỹ thuật; đây là kịch bản ngắn hạn.",
                "risk_notes": [
                    "Chưa phải xác nhận đảo chiều xu hướng chính",
                    "Cần theo dõi volume khi hồi",
                ],
            }
        )

    # STRATEGY_5 — Risk warning (§27)
    if state in ("Distribution / Weakening", "Downtrend"):
        strategies.append(
            {
                "name": "Risk Warning / Exit Alert",
                "signal": "Risk Increasing",
                "confidence": min(90, scores.get("risk_score", 50) + 20),
                "reason": "Cấu trúc suy yếu hoặc giảm: MA, MACD và rủi ro đang tăng.",
                "risk_notes": [
                    "Theo dõi vùng hỗ trợ gần nếu bị thủng",
                    "Không dùng ngôn ngữ tuyệt đối; đây là cảnh báo quản trị rủi ro",
                ],
            }
        )

    if not strategies:
        strategies.append(
            {
                "name": "Observation",
                "signal": "Neutral",
                "confidence": 50,
                "reason": "Chưa có chiến lược nổi trội; tiếp tục theo dõi dữ liệu.",
                "risk_notes": ["Ưu tiên quản trị vị thế và kịch bản"],
            }
        )
    return strategies


def _f(last_row: pd.Series, key: str) -> float | None:
    v = last_row.get(key)
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return float(v)


def build_levels(last_row: pd.Series) -> dict[str, float | None]:
    """
    Mức giá tham chiếu cho UI/AI (§30).
    nearest_* từ cửa sổ 20 phiên; strong_* từ cửa sổ 50 phiên.
    """
    return {
        "nearest_support": _f(last_row, "support_zone"),
        "strong_support": _f(last_row, "lowest_low_50"),
        "nearest_resistance": _f(last_row, "resistance_zone"),
        "strong_resistance": _f(last_row, "highest_high_50"),
    }


def build_risk_layer(scores: dict[str, int], levels: dict[str, float | None]) -> dict:
    """
    risk_level theo risk_score; stop_watch_zone ≈ hỗ trợ gần; invalidation ≈ hỗ trợ mạnh hơn.
    """
    r = scores.get("risk_score", 50)
    if r <= 30:
        level = "Low"
    elif r <= 60:
        level = "Medium"
    else:
        level = "High"
    sup = levels.get("nearest_support")
    return {
        "risk_level": level,
        "stop_watch_zone": sup,
        "invalidation_zone": levels.get("strong_support"),
        "drawdown_risk": "Elevated" if r >= 60 else "Moderate" if r >= 35 else "Contained",
    }
