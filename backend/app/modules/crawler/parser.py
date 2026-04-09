from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any


_MS_DATE = re.compile(r"/Date\((-?\d+)\)/")


def parse_trading_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    m = _MS_DATE.search(s)
    if m:
        ms = int(m.group(1))
        dt = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
        return dt.date()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return date.fromisoformat(s[:10])
    raise ValueError(f"Không parse được ngày: {value!r}")


def normalize_price_row(raw: dict[str, Any]) -> dict[str, Any]:
    td = raw.get("TradingDate") or raw.get("trading_date") or raw.get("date")
    if td is None:
        raise ValueError("Thiếu TradingDate")
    open_p = (
        raw.get("OpenPrice")
        or raw.get("open_price")
        or raw.get("OpenIndex")
        or raw.get("open")
    )
    high_p = (
        raw.get("HighestPrice")
        or raw.get("high_price")
        or raw.get("HighestIndex")
        or raw.get("high")
    )
    low_p = (
        raw.get("LowestPrice")
        or raw.get("low_price")
        or raw.get("LowestIndex")
        or raw.get("low")
    )
    close_p = (
        raw.get("ClosePrice")
        or raw.get("close_price")
        or raw.get("CloseIndex")
        or raw.get("close")
    )
    vol = raw.get("total_volume") or raw.get("TotalVol") or raw.get("volume")
    if open_p is None or high_p is None or low_p is None or close_p is None:
        raise ValueError("Thiếu trường giá bắt buộc")
    if vol is None:
        vol = 0
    return {
        "trading_date": parse_trading_date(td),
        "open_price": float(open_p),
        "high_price": float(high_p),
        "low_price": float(low_p),
        "close_price": float(close_p),
        "price_change": _maybe_float(raw.get("Change") or raw.get("price_change")),
        "percent_change": _maybe_float(raw.get("PerChange") or raw.get("percent_change")),
        "total_volume": int(vol),
        "raw_payload_json": raw,
    }


def _maybe_float(v: Any) -> float | None:
    if v is None:
        return None
    return float(v)
