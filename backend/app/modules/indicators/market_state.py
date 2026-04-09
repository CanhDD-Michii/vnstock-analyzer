"""
Market State Classification (engine doc §20–21).

Mỗi thời điểm gán MỘT trạng thái chính (primary_state).
Thứ tự if quan trọng: ưu tiên tín hiệu mạnh (uptrend/downtrend) trước,
sau đó oversold, weak uptrend, breakout setup, sideway, phân phối, cuối cùng neutral.
"""

from __future__ import annotations

import pandas as pd

from app.modules.indicators.features import last_numeric


def classify_market_state(last_row: pd.Series, scores: dict[str, int]) -> dict[str, str]:
    """
    Phân loại trạng thái dựa trên scores + vài điều kiện giá/MA/RSI/Bollinger/volume.

    Chuỗi điều kiện phản ánh ưu tiên nghiệp vụ (không đối xứng giữa các state).
    """
    trend = scores["trend_score"]
    mom = scores["momentum_score"]
    risk = scores["risk_score"]
    brk = scores["breakout_score"]
    c = last_numeric(last_row, "close")
    sma20 = last_numeric(last_row, "sma_20")
    sma50 = last_numeric(last_row, "sma_50")
    rsi = last_numeric(last_row, "rsi_14")
    bw = last_numeric(last_row, "bollinger_width")
    vr = last_numeric(last_row, "volume_ratio")
    dist_brk = last_numeric(last_row, "distance_to_breakout")
    macd = last_numeric(last_row, "macd")
    sig = last_numeric(last_row, "macd_signal")
    daily_ret = last_numeric(last_row, "daily_return")

    # STATE_1 — Strong Uptrend (§21.1)
    if (
        trend >= 80
        and mom >= 65
        and c > sma20 > 0
        and sma20 > sma50 > 0
        and risk <= 35
    ):
        return {
            "primary_state": "Strong Uptrend",
            "description": "Xu hướng tăng mạnh: điểm xu hướng cao, động lượng tốt và rủi ro thấp.",
        }

    # STATE_6 — Downtrend (§21.6) — xét trước các trạng thái yếu hơn
    if trend < 40 and c < sma20 and sma20 < sma50 and mom < 45 and risk >= 55:
        return {
            "primary_state": "Downtrend",
            "description": "Xu hướng giảm: giá dưới các MA ngắn hạn, động lượng yếu, rủi ro cao.",
        }

    # STATE_7 — Oversold Rebound Candidate (§21.7)
    if rsi < 35 and daily_ret > 0 and c <= sma20:
        return {
            "primary_state": "Oversold Rebound Candidate",
            "description": "Có thể hồi kỹ thuật sau nhịp giảm; chưa xác nhận đảo chiều xu hướng chính.",
        }

    # STATE_2 — Weak Uptrend (§21.2)
    if 60 <= trend < 80 and 50 <= mom < 65 and c > sma20 > 0:
        return {
            "primary_state": "Weak Uptrend",
            "description": "Xu hướng tăng còn nhưng độ mạnh suy giảm, dễ rung lắc.",
        }

    # STATE_4 — Breakout Setup (§21.4)
    if brk >= 60 and dist_brk < 0.02 and vr >= 1.0:
        return {
            "primary_state": "Breakout Setup",
            "description": "Giá áp sát kháng cự, breakout score khá; theo dõi xác nhận thanh khoản.",
        }

    # STATE_3 — Sideway Accumulation (§21.3)
    if 40 <= trend <= 65 and bw < 0.045 and abs(dist_brk) < 0.03:
        return {
            "primary_state": "Sideway Accumulation",
            "description": "Biên độ siết, thanh khoản ổn định; có thể tích lũy trước biến động.",
        }

    # STATE_5 — Distribution / Weakening (§21.5)
    if trend >= 55 and mom < 55 and vr > 1.2 and macd < sig:
        return {
            "primary_state": "Distribution / Weakening",
            "description": "Dấu hiệu phân phối / suy yếu: thanh khoản tăng nhưng động lượng giảm.",
        }

    return {
        "primary_state": "Neutral / Mixed",
        "description": "Tín hiệu trộn; cần thêm xác nhận từ mức giá và dòng tiền.",
    }
