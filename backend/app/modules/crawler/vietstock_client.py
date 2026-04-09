from __future__ import annotations

from collections import deque
from typing import Any

import httpx

DEFAULT_VIETSTOCK_EOD_URL = (
    "https://finance.vietstock.vn/Data/GeneralMarket_GetEODMarketIndexVnForChart"
)

_DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://finance.vietstock.vn",
    "Referer": "https://finance.vietstock.vn/",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}


def _row_has_trading_date(d: dict[str, Any]) -> bool:
    return any(
        k in d for k in ("TradingDate", "trading_date", "date", "Date", "TradingDateStr")
    )


def _discover_price_series(obj: Any, *, max_nodes: int = 8000) -> list[dict[str, Any]]:
    q: deque[Any] = deque([obj])
    seen: set[int] = set()
    nodes = 0
    while q and nodes < max_nodes:
        cur = q.popleft()
        nodes += 1
        oid = id(cur)
        if oid in seen:
            continue
        seen.add(oid)
        if isinstance(cur, list):
            if cur and isinstance(cur[0], dict) and _row_has_trading_date(cur[0]):
                return [x for x in cur if isinstance(x, dict)]
            for x in cur[:80]:
                q.append(x)
        elif isinstance(cur, dict):
            for v in cur.values():
                q.append(v)
    return []


def _follow_path(payload: Any, path: str | list[str | int]) -> Any:
    if isinstance(path, str):
        parts = path.split(".") if "." in path else [path]
    else:
        parts = list(path)
    cur: Any = payload
    for p in parts:
        if isinstance(cur, dict) and str(p) in cur:
            cur = cur[str(p)]
        elif isinstance(cur, dict) and p in cur:
            cur = cur[p]  # type: ignore[index]
        elif isinstance(cur, list) and isinstance(p, int) and 0 <= p < len(cur):
            cur = cur[p]
        else:
            return None
    return cur


def extract_price_series_from_payload(payload: Any, metadata: dict[str, Any]) -> list[dict[str, Any]]:
    path = metadata.get("response_path")
    if path:
        cur = _follow_path(payload, path)  # type: ignore[arg-type]
        if isinstance(cur, list) and cur and isinstance(cur[0], dict):
            return [x for x in cur if isinstance(x, dict)]

    keys = metadata.get("response_series_keys") or [
        "data",
        "Data",
        "d",
        "Result",
        "result",
        "chart",
        "Chart",
        "Series",
        "series",
    ]
    if isinstance(payload, dict):
        for k in keys:
            v = payload.get(k)
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return [x for x in v if isinstance(x, dict)]

    return _discover_price_series(payload)


def _merge_form(
    metadata: dict[str, Any],
    *,
    request_verification_token: str | None,
    extra_form: dict[str, str] | None,
) -> dict[str, str]:
    base = metadata.get("form") or {}
    out: dict[str, str] = {str(k): str(v) for k, v in base.items()}
    if extra_form:
        out.update({str(k): str(v) for k, v in extra_form.items()})
    token = request_verification_token
    if token is None:
        sess = metadata.get("session")
        if isinstance(sess, dict):
            token = sess.get("__RequestVerificationToken") or sess.get(
                "requestVerificationToken"
            )
    if token:
        out["__RequestVerificationToken"] = str(token)
    return out


def _resolve_cookie(metadata: dict[str, Any], cookie_override: str | None) -> str | None:
    if cookie_override and cookie_override.strip():
        return cookie_override.strip()
    sess = metadata.get("session")
    if isinstance(sess, dict) and sess.get("cookie"):
        return str(sess["cookie"]).strip()
    return None


def fetch_vietstock_price_series(
    metadata: dict[str, Any],
    *,
    cookie: str | None = None,
    request_verification_token: str | None = None,
    extra_form: dict[str, str] | None = None,
    timeout: float = 90.0,
) -> list[dict[str, Any]]:
    if not isinstance(metadata, dict):
        raise ValueError("crawlMetadata phải là object JSON")

    url = str(metadata.get("url") or DEFAULT_VIETSTOCK_EOD_URL)
    form = _merge_form(
        metadata,
        request_verification_token=request_verification_token,
        extra_form=extra_form,
    )
    if "__RequestVerificationToken" not in form:
        raise ValueError(
            "Thiếu __RequestVerificationToken (gửi kèm request hoặc lưu trong crawlMetadata.session)"
        )

    headers = {**_DEFAULT_HEADERS, **(metadata.get("headers") or {})}
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
        payload = r.json()
    except ValueError as e:
        raise ValueError("Không parse được JSON từ VietStock") from e

    series = extract_price_series_from_payload(payload, metadata)
    return series
