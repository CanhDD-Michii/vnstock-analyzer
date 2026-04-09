"""Hiệu suất giá D/W/M/Q/YTD/Y từ chuỗi nến lịch sử (đóng cửa), sắp xếp theo ngày tăng dần."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


def _bar_date(b: dict[str, Any]) -> date:
    d = b["trading_date"]
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        return date.fromisoformat(str(d)[:10])
    raise TypeError(f"trading_date không hợp lệ: {type(d)!r}")


def _close_on_or_before(bars_asc: list[dict[str, Any]], target: date) -> float | None:
    best: float | None = None
    for b in bars_asc:
        if _bar_date(b) <= target:
            best = float(b["close_price"])
    return best


def _pct_change(last: float, base: float | None) -> float | None:
    if base is None or base == 0:
        return None
    return round((last - base) / base * 100, 4)


def compute_performance_from_bars(bars_asc: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Trả về close mới nhất và % so với: phiên trước, ~7 ngày, ~30 ngày, ~92 ngày,
    phiên đầu năm (YTD), ~365 ngày lịch.
    """
    empty = {
        "as_of_date": None,
        "close_price": None,
        "pct_day": None,
        "pct_week": None,
        "pct_month": None,
        "pct_quarter": None,
        "pct_ytd": None,
        "pct_year": None,
    }
    if not bars_asc:
        return empty

    last = bars_asc[-1]
    last_close = float(last["close_price"])
    last_date = _bar_date(last)

    pct_day = None
    if len(bars_asc) >= 2:
        pct_day = _pct_change(last_close, float(bars_asc[-2]["close_price"]))

    ref_w = _close_on_or_before(bars_asc, last_date - timedelta(days=7))
    ref_m = _close_on_or_before(bars_asc, last_date - timedelta(days=30))
    ref_q = _close_on_or_before(bars_asc, last_date - timedelta(days=92))
    ref_y = _close_on_or_before(bars_asc, last_date - timedelta(days=365))

    first_close_ytd: float | None = None
    for b in bars_asc:
        if _bar_date(b).year == last_date.year:
            first_close_ytd = float(b["close_price"])
            break

    return {
        "as_of_date": last_date,
        "close_price": last_close,
        "pct_day": pct_day,
        "pct_week": _pct_change(last_close, ref_w),
        "pct_month": _pct_change(last_close, ref_m),
        "pct_quarter": _pct_change(last_close, ref_q),
        "pct_ytd": _pct_change(last_close, first_close_ytd),
        "pct_year": _pct_change(last_close, ref_y),
    }
