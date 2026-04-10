"""
Gộp chỉ số cơ bản 12 khóa: ưu tiên stock_key_metrics, bổ sung từ BCTC và P/E-P/B suy ra từ giá đóng.

Các khóa (đồng bộ fundamental_context.FUNDAMENTAL_NUMERIC_KEYS):
  pe, pb, roe, roa, gross_margin, net_margin, debt_to_equity,
  current_ratio, quick_ratio, revenue_growth_yoy, profit_growth_yoy, eps_growth_yoy
"""

from __future__ import annotations

from typing import Any

from app.modules.indicators.fundamental_context import FUNDAMENTAL_NUMERIC_KEYS


def _num(x: Any) -> float | None:
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if v != v:  # NaN
        return None
    return v


def _pct_change(cur: float | None, prev: float | None) -> float | None:
    if cur is None or prev is None:
        return None
    if prev == 0:
        return None
    return round(((cur - prev) / abs(prev)) * 100.0, 4)


def _ratios_from_single_report(fin: dict[str, Any]) -> dict[str, float | None]:
    revenue = _num(fin.get("revenue"))
    gp = _num(fin.get("gross_profit"))
    np = _num(fin.get("net_profit"))
    eq = _num(fin.get("equity"))
    ta = _num(fin.get("total_assets"))
    tl = _num(fin.get("total_liabilities"))

    gross_margin = None
    if revenue is not None and revenue != 0 and gp is not None:
        gross_margin = round((gp / revenue) * 100.0, 4)

    net_margin = None
    if revenue is not None and revenue != 0 and np is not None:
        net_margin = round((np / revenue) * 100.0, 4)

    roe = None
    if eq is not None and eq != 0 and np is not None:
        roe = round((np / eq) * 100.0, 4)

    roa = None
    if ta is not None and ta != 0 and np is not None:
        roa = round((np / ta) * 100.0, 4)

    debt_to_equity = None
    if eq is not None and eq != 0 and tl is not None:
        debt_to_equity = round(tl / eq, 4)

    return {
        "gross_margin": gross_margin,
        "net_margin": net_margin,
        "roe": roe,
        "roa": roa,
        "debt_to_equity": debt_to_equity,
    }


def _yoy_from_pair(
    cur: dict[str, Any],
    prev: dict[str, Any],
) -> dict[str, float | None]:
    return {
        "revenue_growth_yoy": _pct_change(_num(cur.get("revenue")), _num(prev.get("revenue"))),
        "profit_growth_yoy": _pct_change(_num(cur.get("net_profit")), _num(prev.get("net_profit"))),
        "eps_growth_yoy": _pct_change(_num(cur.get("eps")), _num(prev.get("eps"))),
    }


def _implied_pe_pb(
    close: float | None,
    eps: float | None,
    bvps: float | None,
) -> tuple[float | None, float | None]:
    pe = None
    pb = None
    if close is not None and close > 0 and eps is not None and eps > 0:
        pe = round(close / eps, 4)
    if close is not None and close > 0 and bvps is not None and bvps > 0:
        pb = round(close / bvps, 4)
    return pe, pb


def build_merged_fundamental_metrics(
    *,
    db_metrics: dict[str, Any] | None,
    latest_fin: dict[str, Any] | None,
    previous_fin: dict[str, Any] | None,
    latest_close: float | None,
) -> dict[str, Any] | None:
    """
    Trả về dict gồm metric_date (nếu có từ DB) + 12 khóa số; None nếu không có bất kỳ giá trị số nào.
    Thứ tự ưu tiên: DB → suy từ BCTC (tỷ số, YoY) → P/E, P/B từ giá đóng & EPS/BVPS BCTC mới nhất.
    """
    derived: dict[str, float | None] = {k: None for k in FUNDAMENTAL_NUMERIC_KEYS}

    if latest_fin:
        for k, v in _ratios_from_single_report(latest_fin).items():
            derived[k] = v
        if previous_fin:
            for k, v in _yoy_from_pair(latest_fin, previous_fin).items():
                derived[k] = v

    implied_pe, implied_pb = _implied_pe_pb(
        latest_close,
        _num(latest_fin.get("eps")) if latest_fin else None,
        _num(latest_fin.get("bvps")) if latest_fin else None,
    )
    if derived.get("pe") is None:
        derived["pe"] = implied_pe
    if derived.get("pb") is None:
        derived["pb"] = implied_pb

    out: dict[str, Any] = {}
    db = db_metrics or {}
    if db.get("metric_date") is not None:
        out["metric_date"] = db["metric_date"]

    for k in FUNDAMENTAL_NUMERIC_KEYS:
        db_v = db.get(k)
        if db_v is not None:
            try:
                out[k] = float(db_v)
            except (TypeError, ValueError):
                out[k] = derived.get(k)
        else:
            out[k] = derived.get(k)

    if not any(out.get(k) is not None for k in FUNDAMENTAL_NUMERIC_KEYS):
        return None
    return out
