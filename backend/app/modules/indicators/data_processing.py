"""
Lớp xử lý dữ liệu đầu vào (Data Processing Layer — engine doc §5).

Nhiệm vụ: chuẩn hóa cột, sắp xếp thời gian, loại trùng ngày, kiểm tra OHLCV,
bổ sung prev_close / biến động giá phục vụ feature phía sau.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from app.core.exceptions import AppError


def bars_to_dataframe(bars: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Chuyển danh sách bản ghi DB (open_price, trading_date, …) sang DataFrame chuẩn.

    - Sort tăng dần theo ngày, giữ bản ghi cuối nếu trùng ngày.
    - Validate: high >= max(O,C,L), low <= min(O,C,H), volume >= 0.
    """
    if not bars:
        raise AppError("Không có dữ liệu giá", "NO_PRICE_DATA")
    rows = []
    for b in bars:
        rows.append(
            {
                "date": b["trading_date"]
                if isinstance(b["trading_date"], date)
                else pd.to_datetime(b["trading_date"]).date(),
                "open": float(b["open_price"]),
                "high": float(b["high_price"]),
                "low": float(b["low_price"]),
                "close": float(b["close_price"]),
                "volume": int(b["total_volume"] or 0),
            }
        )
    df = pd.DataFrame(rows)
    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    df = df.reset_index(drop=True)
    _validate_ohlcv(df)

    # Trường cơ sở theo §5.2.3 engine doc
    df["prev_close"] = df["close"].shift(1)
    df["price_change"] = df["close"] - df["prev_close"]
    df["price_change_pct"] = np.where(
        df["prev_close"].replace(0, np.nan).notna(),
        (df["close"] / df["prev_close"] - 1.0) * 100.0,
        np.nan,
    )
    return df


def _validate_ohlcv(df: pd.DataFrame) -> None:
    """Kiểm tra chất lượng nến: biên high/low bao trùm open/close, volume không âm."""
    bad = (
        (df["high"] < df[["open", "close", "low"]].max(axis=1))
        | (df["low"] > df[["open", "close", "high"]].min(axis=1))
        | (df["volume"] < 0)
    )
    if bad.any():
        raise AppError("Dữ liệu OHLCV không hợp lệ", "INVALID_OHLCV")
