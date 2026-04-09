"""
Xây dựng prompt cho lớp AI Interpretation (engine doc §32 + STOCK_ANALYSIS_STRATEGY).

- System prompt: khóa vai trò, cấm bịa số, cấm khuyến nghị tuyệt đối.
- User template: nhét JSON engine đã tính; AI chỉ diễn giải có cấu trúc.
"""

from __future__ import annotations

import json
from typing import Any

DEFAULT_SYSTEM_PROMPT = """Bạn là chuyên gia phân tích cổ phiếu Việt Nam. Bạn chỉ được luận giải dựa trên
JSON dữ liệu hệ thống cung cấp (điểm số, trạng thái thị trường, chiến lược đang active, hỗ trợ/kháng cự, rủi ro).
Tuyệt đối không bịa số liệu, không đưa ra khuyến nghị chắc chắn mua/bán. Dùng tiếng Việt rõ ràng, chia section.
Trả về đúng một JSON object theo schema yêu cầu, không markdown."""

DEFAULT_USER_TEMPLATE = """Dưới đây là payload phân tích đã được engine tính sẵn (OHLCV, chỉ báo, score, state, strategies).
Hãy viết luận giải cho nhà đầu tư theo 4 phần nội dung trong summary: xu hướng hiện tại; dòng tiền/động lượng; vùng giá quan trọng; rủi ro cần lưu ý.
Đồng thời điền các field structured khác chỉ dựa trên dữ liệu JSON.

PAYLOAD:
{{payload_json}}
"""


def build_user_message(payload: dict[str, Any], template: str | None = None) -> str:
    """Thay placeholder bằng JSON payload (UTF-8, indent để model đọc cấu trúc)."""
    t = template or DEFAULT_USER_TEMPLATE
    return t.replace("{{payload_json}}", json.dumps(payload, ensure_ascii=False, indent=2))


def openai_output_schema_hint() -> str:
    """Gợi ý schema JSON (kèm response_format json_object ở client)."""
    return json.dumps(
        {
            "summary": "string — 4 phần: xu hướng; dòng tiền/động lượng; vùng quan trọng; rủi ro",
            "fundamental_analysis": "string — nếu không có dữ liệu cơ bản, nêu rõ là chưa có",
            "technical_analysis": "string — dựa trên scores/state/indicators",
            "risks": ["string"],
            "conclusion": "string",
            "recommendation": "BUY | WATCH | HOLD | AVOID (chữ HOA, rule-based gợi ý từ score)",
        },
        ensure_ascii=False,
    )
