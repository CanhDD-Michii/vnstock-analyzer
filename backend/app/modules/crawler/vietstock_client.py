from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import httpx

from app.modules.crawler.parser import parse_trading_date

DEFAULT_VIETSTOCK_LIST_PRICE_URL = (
    "https://finance.vietstock.vn/data/GetStockDeal_ListPriceByTimeFrame"
)

"""Chỉ các field được gửi trong body x-www-form-urlencoded (curl DevTools)."""
_LIST_PRICE_FORM_KEYS = frozenset(
    {
        "stockCode",
        "timeFrame",
        "toDate",
        "page",
        "pageSize",
        "languageID",
        "__RequestVerificationToken",
    }
)

_DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://finance.vietstock.vn",
    "Pragma": "no-cache",
    "Referer": "https://finance.vietstock.vn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}


def _merge_vietstock_headers(
    metadata: dict[str, Any],
    *,
    cookie: str | None,
    stock_code: str | None = None,
) -> dict[str, str]:
    raw = metadata.get("headers")
    extra: dict[str, str] = {}
    if isinstance(raw, dict):
        extra = {str(k): str(v) for k, v in raw.items()}
    headers = {**_DEFAULT_HEADERS, **extra}
    if "Referer" not in extra and stock_code:
        tpl = metadata.get("referer_template")
        if isinstance(tpl, str) and tpl.strip():
            headers["Referer"] = (
                tpl.replace("{stockCode}", stock_code).replace("{ticker}", stock_code)
            )
        else:
            headers["Referer"] = (
                f"https://finance.vietstock.vn/{stock_code}/thong-ke-giao-dich.htm"
            )
    return headers


def _resolve_cookie(metadata: dict[str, Any], cookie_override: str | None) -> str | None:
    if cookie_override and cookie_override.strip():
        return cookie_override.strip()
    sess = metadata.get("session")
    if isinstance(sess, dict) and sess.get("cookie"):
        return str(sess["cookie"]).strip()
    return None


def _post_vietstock_json(
    metadata: dict[str, Any],
    url: str,
    form: dict[str, str],
    *,
    cookie: str | None,
    timeout: float,
    stock_code: str | None = None,
) -> Any:
    if "__RequestVerificationToken" not in form:
        raise ValueError(
            "Thiếu __RequestVerificationToken (gửi kèm request hoặc lưu trong crawlMetadata.session)"
        )
    headers = _merge_vietstock_headers(metadata, cookie=cookie, stock_code=stock_code)
    ck = _resolve_cookie(metadata, cookie)
    if ck:
        headers["Cookie"] = ck
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        try:
            r = client.post(url, data=form, headers=headers)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"VietStock trả HTTP {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise ValueError(f"Lỗi kết nối VietStock: {e!s}") from e
    text = (r.text or "").strip()
    if not text or text[0] not in "{[":
        raise ValueError(
            "Phản hồi không phải JSON (thường do thiếu Cookie hợp lệ hoặc token hết hạn)"
        )
    try:
        return r.json()
    except ValueError as e:
        raise ValueError("Không parse được JSON từ VietStock") from e


def extract_list_price_results(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            lst = data.get("ListPrice_Results")
            if isinstance(lst, list):
                return [x for x in lst if isinstance(x, dict)]
    return []


def _merge_list_price_form(
    metadata: dict[str, Any],
    stock_code: str,
    to_date_iso: str,
    page_size: int,
    *,
    request_verification_token: str | None,
    extra_form: dict[str, str] | None,
) -> dict[str, str]:
    base = metadata.get("form")
    if not isinstance(base, dict):
        base = {}

    out: dict[str, str] = {}
    for key in ("timeFrame", "languageID"):
        if key in base and str(base[key]).strip():
            out[key] = str(base[key])

    if extra_form:
        for k, v in extra_form.items():
            sk = str(k)
            if sk in _LIST_PRICE_FORM_KEYS and sk != "__RequestVerificationToken":
                out[sk] = str(v)

    out["stockCode"] = stock_code
    out["toDate"] = to_date_iso
    out["page"] = "1"
    out["pageSize"] = str(page_size)
    out.setdefault("timeFrame", "C")
    out.setdefault("languageID", "1")

    token = request_verification_token
    if token is None:
        sess = metadata.get("session")
        if isinstance(sess, dict):
            token = sess.get("__RequestVerificationToken") or sess.get(
                "requestVerificationToken"
            )
    if token:
        out["__RequestVerificationToken"] = str(token)

    return {k: v for k, v in out.items() if k in _LIST_PRICE_FORM_KEYS}


def fetch_vietstock_list_price_backward(
    metadata: dict[str, Any],
    stock_code: str,
    *,
    cookie: str | None = None,
    request_verification_token: str | None = None,
    extra_form: dict[str, str] | None = None,
    initial_to_date: date,
    timeout: float = 90.0,
) -> list[dict[str, Any]]:
    """POST ListPrice theo toDate, lùi: mỗi vòng min(TradingDate) − 1 ngày."""
    if not isinstance(metadata, dict):
        raise ValueError("crawlMetadata phải là object JSON")
    url = str(metadata.get("url") or "").strip() or DEFAULT_VIETSTOCK_LIST_PRICE_URL
    strat = metadata.get("crawl_strategy")
    if not isinstance(strat, dict):
        strat = {}
    max_rounds = int(strat.get("max_rounds", 500))
    page_size = int(strat.get("page_size") or metadata.get("page_size") or 20)
    if page_size > 20:
        page_size = 20
    if page_size < 1:
        page_size = 1

    merged: dict[date, dict[str, Any]] = {}
    to_date = initial_to_date
    for _ in range(max(1, max_rounds)):
        form = _merge_list_price_form(
            metadata,
            stock_code,
            to_date.isoformat(),
            page_size,
            request_verification_token=request_verification_token,
            extra_form=extra_form,
        )
        payload = _post_vietstock_json(
            metadata, url, form, cookie=cookie, timeout=timeout, stock_code=stock_code
        )
        batch = extract_list_price_results(payload)
        if not batch:
            break
        batch_dates: list[date] = []
        for row in batch:
            td = row.get("TradingDate")
            if td is None:
                continue
            try:
                d = parse_trading_date(td)
            except (TypeError, ValueError):
                continue
            batch_dates.append(d)
            merged.setdefault(d, row)
        if not batch_dates:
            break
        min_d = min(batch_dates)
        next_to = min_d - timedelta(days=1)
        if next_to >= to_date:
            break
        to_date = next_to
    return list(merged.values())
