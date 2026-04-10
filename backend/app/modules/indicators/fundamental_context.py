"""
Bối cảnh cơ bản cho prompt AI: metrics đã có, thiếu gì, nhãn tiếng Việt.

`fundamental_metrics` trong engine có thể null nếu chưa crawl key metrics —
prompt cũ khiến model luôn trả một câu "chưa đủ dữ liệu". Khối này làm rõ
từng trường kỳ vọng và phần trăm coverage để model luận giải có cấu trúc.
"""

from __future__ import annotations

from typing import Any

# Trùng với metrics_to_dict (trừ metric_date — ngày snapshot)
FUNDAMENTAL_NUMERIC_KEYS: tuple[str, ...] = (
    "pe",
    "pb",
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "debt_to_equity",
    "current_ratio",
    "quick_ratio",
    "revenue_growth_yoy",
    "profit_growth_yoy",
    "eps_growth_yoy",
)

FUNDAMENTAL_FIELD_LABELS_VI: dict[str, str] = {
    "pe": "P/E — giá trên lãi cơ bản (định giá)",
    "pb": "P/B — giá trên giá trị sổ sách",
    "roe": "ROE (%) — sinh lời trên vốn chủ",
    "roa": "ROA (%) — sinh lời trên tài sản",
    "gross_margin": "Biên lợi nhuận gộp (%)",
    "net_margin": "Biên lợi nhuận ròng (%)",
    "debt_to_equity": "Nợ/vốn chủ (đòn bẩy)",
    "current_ratio": "Hệ số thanh toán hiện hành",
    "quick_ratio": "Hệ số thanh toán nhanh",
    "revenue_growth_yoy": "Tăng trưởng doanh thu YoY (%)",
    "profit_growth_yoy": "Tăng trưởng lợi nhuận YoY (%)",
    "eps_growth_yoy": "Tăng trưởng EPS YoY (%)",
}


def _present_keys(metrics: dict[str, Any] | None) -> list[str]:
    if not metrics:
        return []
    return [k for k in FUNDAMENTAL_NUMERIC_KEYS if metrics.get(k) is not None]


def _missing_keys(metrics: dict[str, Any] | None) -> list[str]:
    if not metrics:
        return list(FUNDAMENTAL_NUMERIC_KEYS)
    return [k for k in FUNDAMENTAL_NUMERIC_KEYS if metrics.get(k) is None]


def build_fundamental_context(
    *,
    ticker: str,
    company_name: str,
    exchange: str,
    sector: str,
    description: str | None,
    metrics_dict: dict[str, Any] | None,
    latest_financial_report: dict[str, Any] | None,
    fundamental_score_0_100: int | None,
    key_metrics_row_present: bool = False,
) -> dict[str, Any]:
    present = _present_keys(metrics_dict)
    missing = _missing_keys(metrics_dict)
    n = len(FUNDAMENTAL_NUMERIC_KEYS)
    ratio = round(len(present) / n, 4) if n else 0.0
    desc = (description or "").strip()
    desc_excerpt = desc[:800] + ("…" if len(desc) > 800 else "") if desc else None

    return {
        "ticker": ticker,
        "company_profile": {
            "name": company_name,
            "exchange": exchange,
            "sector": sector,
            "description_excerpt": desc_excerpt,
        },
        "key_metrics_snapshot": metrics_dict,
        "has_key_metrics_row": key_metrics_row_present,
        "latest_financial_report": latest_financial_report,
        "has_financial_report_row": latest_financial_report is not None,
        "fundamental_score_0_100": fundamental_score_0_100,
        "expected_numeric_keys": list(FUNDAMENTAL_NUMERIC_KEYS),
        "field_labels_vi": {k: FUNDAMENTAL_FIELD_LABELS_VI[k] for k in FUNDAMENTAL_NUMERIC_KEYS},
        "present_numeric_keys": present,
        "missing_numeric_keys": missing,
        "coverage_numeric_ratio": ratio,
        "interpretation_hints": (
            "fundamental_score_0_100 là điểm nội bộ 0–100 từ các metrics có sẵn (xem compute_fundamental_score); "
            "None nếu không có metrics để chấm."
        ),
    }
