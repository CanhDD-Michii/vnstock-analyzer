"""
Điểm cơ bản 0–100 từ bảng key metrics (STOCK_ANALYSIS_STRATEGY — mục 16 & lớp dữ liệu 2).

Trọng số gợi ý (tổng tối đa ~100 sau clip):
  - tăng trưởng doanh thu / lợi nhuận
  - ROE, đòn bẩy (debt/equity), biên lợi nhuận
  - định giá P/E, P/B

Nếu không có metrics → None (AI/engine phải nêu rõ “chưa có dữ liệu cơ bản”).
"""

from __future__ import annotations

from typing import Any


def compute_fundamental_score(metrics: dict[str, Any] | None) -> int | None:
    """Cộng điểm theo ngưỡng; kết quả luôn trong [0, 100]."""
    if not metrics:
        return None
    score = 0.0
    rg = metrics.get("revenue_growth_yoy")
    pg = metrics.get("profit_growth_yoy")
    roe = metrics.get("roe")
    de = metrics.get("debt_to_equity")
    gm = metrics.get("gross_margin")
    nm = metrics.get("net_margin")
    pe = metrics.get("pe")
    pb = metrics.get("pb")

    if rg is not None:
        score += 15 if float(rg) >= 10 else 10 if float(rg) >= 0 else 0
    if pg is not None:
        score += 20 if float(pg) >= 10 else 12 if float(pg) >= 0 else 0
    if roe is not None:
        r = float(roe)
        score += 20 if r >= 15 else 12 if r >= 8 else 4
    if de is not None:
        d = float(de)
        score += 15 if d <= 0.5 else 10 if d <= 1.0 else 4
    if gm is not None:
        score += 8 if float(gm) >= 30 else 4
    if nm is not None:
        score += 7 if float(nm) >= 10 else 4
    if pe is not None and pb is not None:
        pev, pbv = float(pe), float(pb)
        val = 0.0
        if pev <= 15:
            val += 8
        elif pev <= 25:
            val += 5
        if pbv <= 2:
            val += 7
        elif pbv <= 4:
            val += 4
        score += min(15, val)

    return int(max(0, min(100, round(score))))
