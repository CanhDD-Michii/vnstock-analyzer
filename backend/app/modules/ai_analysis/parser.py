from __future__ import annotations

import json
import re
from typing import Any

from app.modules.ai_analysis.exceptions import OpenAIResponseFormatError


def _coerce_analysis_text(val: Any) -> str:
    """Chuỗi hiển thị an toàn: model đôi khi trả object thay vì string → tránh [object Object]."""
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, (int, float, bool)):
        return str(val)
    if isinstance(val, list):
        lines = [_coerce_analysis_text(x).strip() for x in val]
        return "\n".join(line for line in lines if line)
    if isinstance(val, dict):
        parts: list[str] = []
        for k, v in val.items():
            label = str(k).strip() or "—"
            body = _coerce_analysis_text(v).strip()
            if body:
                parts.append(f"{label}\n{body}")
        return "\n\n".join(parts)
    return json.dumps(val, ensure_ascii=False)


def _normalize_risks_list(risks: Any) -> list[str]:
    if not isinstance(risks, list):
        return []
    out: list[str] = []
    for item in risks:
        t = _coerce_analysis_text(item).strip()
        if t:
            out.append(t)
    return out


def parse_ai_json_response(content: str) -> dict[str, Any]:
    text = content.strip()
    m = re.search(r"\{[\s\S]*\}\s*$", text)
    if m:
        text = m.group(0)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OpenAIResponseFormatError("Không parse được JSON từ OpenAI") from exc
    required = [
        "summary",
        "fundamental_analysis",
        "technical_analysis",
        "risks",
        "conclusion",
        "recommendation",
    ]
    for k in required:
        if k not in data:
            raise OpenAIResponseFormatError(f"Thiếu field: {k}")
    if not isinstance(data["risks"], list):
        raise OpenAIResponseFormatError("risks phải là mảng")
    for key in ("fundamental_data_gaps", "fundamental_wishlist"):
        if key in data and data[key] is not None and not isinstance(data[key], list):
            raise OpenAIResponseFormatError(f"{key} phải là mảng (hoặc bỏ key)")
    data.setdefault("fundamental_data_gaps", [])
    data.setdefault("fundamental_wishlist", [])
    for text_key in (
        "summary",
        "fundamental_analysis",
        "technical_analysis",
        "conclusion",
    ):
        data[text_key] = _coerce_analysis_text(data.get(text_key))
    data["risks"] = _normalize_risks_list(data.get("risks"))
    for list_key in ("fundamental_data_gaps", "fundamental_wishlist"):
        raw = data.get(list_key)
        if isinstance(raw, list):
            data[list_key] = [
                s for s in (_coerce_analysis_text(x).strip() for x in raw) if s
            ]
        else:
            data[list_key] = []
    return data
