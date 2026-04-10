"""
Xây dựng prompt cho lớp AI Interpretation (engine doc §32 + STOCK_ANALYSIS_STRATEGY).

- System prompt: khóa vai trò, cấm bịa số, cấm khuyến nghị tuyệt đối.
- User template: nhét JSON engine đã tính; AI chỉ diễn giải có cấu trúc.
"""

from __future__ import annotations

import json
from typing import Any

# Mã khuyến nghị trong JSON (UI/FE dịch sang tiếng Việt) — đồng bộ với frontend/lib/ai-recommendation.ts
RECOMMENDATION_CODES_DOC = """- BUY → Nên mua
- SELL → Nên bán
- STRONG_BUY → Mua mạnh
- STRONG_SELL → Bán mạnh
- HOLD → Nên giữ
- WATCH → Theo dõi
- AVOID → Tránh / không nên mua
- NEUTRAL → Trung lập"""

ALLOWED_RECOMMENDATION_CODES = (
    "BUY | SELL | STRONG_BUY | STRONG_SELL | HOLD | WATCH | AVOID | NEUTRAL"
)

DEFAULT_SYSTEM_PROMPT = f"""Bạn là chuyên gia phân tích cổ phiếu thị trường Việt Nam (vai trò: diễn giải dữ liệu, không phải tư vấn đầu tư có thù lao).

QUY TẮC BẮT BUỘC:
1) Chỉ luận giải dựa trên JSON payload hệ thống gửi kèm (điểm số, state, strategies, mức giá, rủi ro…). Không bịa thêm số, mã, tin tức, giá thực địa hoặc sự kiện không có trong JSON.
2) Mọi văn bản hiển thị cho người dùng (summary, fundamental_analysis, technical_analysis, risks, conclusion) viết bằng tiếng Việt, rõ ràng, giọng trung lập, dễ đọc.
3) Không dùng ngôn ngữ chắc chắn kiểu "chắc chắn tăng/giảm", "nhất định mua/bán". Luôn nhắc rủi ro và giới hạn của mô hình.
4) Trả về ĐÚNG MỘT object JSON hợp lệ (không markdown, không bọc ```, không text thừa ngoài JSON).
5) Không suy luận vượt quá dữ liệu. 
Nếu payload không chứa thông tin → phải ghi rõ là "không có trong payload".
Không được dùng kiến thức bên ngoài (tin tức, kinh nghiệm thị trường, giả định).
6) Trường "recommendation" chỉ ghi ĐÚNG MỘT mã tiếng Anh IN HOA (không tiếng Việt trong giá trị JSON), chọn trong danh sách sau (mỗi dòng: mã → nghĩa hiển thị cho người dùng):
{RECOMMENDATION_CODES_DOC}
Không dùng mã khác, không gạch dưới sai (vd. STRONG BUY), không khoảng trắng thừa.
7) Quy tắc chọn recommendation (bắt buộc):
- STRONG_BUY: khi đa số scores cao + state bullish rõ ràng + rủi ro thấp
- BUY: khi xu hướng tích cực nhưng chưa đủ mạnh
- HOLD: khi trung tính nhưng không xấu
- WATCH: khi tín hiệu chưa rõ hoặc thiếu dữ liệu
- SELL: khi xu hướng tiêu cực
- STRONG_SELL: khi tín hiệu giảm mạnh rõ ràng
- AVOID: khi rủi ro cao hoặc dữ liệu xấu
- NEUTRAL: khi tín hiệu mâu thuẫn"""

DEFAULT_USER_TEMPLATE = f"""Bạn nhận payload JSON dưới đây — đã được engine tính sẵn (OHLCV, chỉ báo, điểm, trạng thái thị trường, chiến lược, mức hỗ trợ/kháng cự nếu có).

NHIỆM VỤ:
- summary (một chuỗi tiếng Việt, có thể xuống dòng): tóm tắt 4 ý — (1) xu hướng hiện tại theo state/scores; (2) dòng tiền / động lượng nếu có trong dữ liệu; (3) vùng giá quan trọng (hỗ trợ, kháng cự, tham chiếu từ payload); (4) rủi ro chính cần lưu ý.
- fundamental_analysis: đánh giá cơ bản từ các trường fundamental/metrics trong payload; nếu thiếu dữ liệu cơ bản, nêu rõ "Chưa đủ dữ liệu cơ bản trong payload" và không suy diễn.
- technical_analysis: luận giải kỹ thuật dựa trên scores, state, indicators/strategies trong payload, không thêm chỉ báo không có trong JSON.
- risks: mảng các chuỗi tiếng Việt (ít nhất 1 mục), mỗi mục một rủi ro cụ thể, gắn với dữ liệu đã cho.
- conclusion: kết luận ngắn gọn, trung lập, tiếng Việt.
- recommendation: chọn ĐÚNG MỘT mã trong {{ {ALLOWED_RECOMMENDATION_CODES} }} — tương ứng nghĩa tiếng Việt:
{RECOMMENDATION_CODES_DOC}
  Chọn mã phù hợp độ mạnh tín hiệu và rủi ro (vd. STRONG_BUY/STRONG_SELL chỉ khi scores/state thống nhất rất rõ; NEUTRAL khi tín hiệu lẫn lộn; WATCH khi cần thêm dữ liệu hoặc biên độ mơ hồ; AVOID khi rủi ro cao theo payload).

PAYLOAD:
{{{{payload_json}}}}
"""


def build_user_message(payload: dict[str, Any], template: str | None = None) -> str:
    """Thay placeholder bằng JSON payload (UTF-8, indent để model đọc cấu trúc)."""
    t = template or DEFAULT_USER_TEMPLATE
    return t.replace("{{payload_json}}", json.dumps(payload, ensure_ascii=False, indent=2))


def openai_output_schema_hint() -> str:
    """Gợi ý schema JSON (kèm response_format json_object ở client)."""
    return json.dumps(
        {
            "summary": "string (tiếng Việt) — 4 phần: xu hướng; dòng tiền/động lượng; vùng giá quan trọng; rủi ro. Mỗi risk phải liên kết trực tiếp tới field trong payload (score, indicator, state...). - Không được viết rủi ro chung chung không có trong dữ liệu",
            "fundamental_analysis": "string (tiếng Việt) — từ dữ liệu cơ bản trong payload hoặc nêu thiếu dữ liệu",
            "technical_analysis": "string (tiếng Việt) — scores/state/indicators trong payload",
            "risks": ["string (tiếng Việt) — ít nhất 1 phần tử"],
            "conclusion": "string (tiếng Việt) — ngắn gọn, trung lập",
            "recommendation": (
                f"CHỈ MỘT TRONG: {ALLOWED_RECOMMENDATION_CODES} "
                "(chữ HOA; nghĩa UI: BUY Nên mua; SELL Nên bán; STRONG_BUY Mua mạnh; "
                "STRONG_SELL Bán mạnh; HOLD Nên giữ; WATCH Theo dõi; AVOID Tránh/không nên mua; NEUTRAL Trung lập)"
            ),
        },
        ensure_ascii=False,
    )
