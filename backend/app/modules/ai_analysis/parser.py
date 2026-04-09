from __future__ import annotations

import json
import re
from typing import Any

from app.modules.ai_analysis.exceptions import OpenAIResponseFormatError


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
    return data
