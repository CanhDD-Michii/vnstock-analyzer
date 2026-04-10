"""
AI Interpretation Prompt Builder (Production-grade)

Mục tiêu:
- AI chỉ DIỄN GIẢI (không phân tích thô)
- Không hallucination
- Có bias rõ ràng (tránh neutral vô nghĩa)
- Lập luận sâu (indicator → meaning → action)
- Có short-term / long-term
"""

from __future__ import annotations

import json
from typing import Any

# =========================
# RECOMMENDATION
# =========================

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

# =========================
# SYSTEM PROMPT (CORE LOGIC)
# =========================

DEFAULT_SYSTEM_PROMPT = f"""
Bạn là chuyên gia phân tích cổ phiếu Việt Nam.
Vai trò: DIỄN GIẢI dữ liệu từ hệ thống, KHÔNG phải tư vấn đầu tư có thù lao.

=========================
(A) QUY TẮC TUYỆT ĐỐI — DỮ LIỆU
=========================

1. CHỈ dùng JSON payload (engine, fundamental_context nếu có).
- Không bịa số, tin, mã ngoài payload.
- Thiếu field → ghi "Không có trong payload" (đúng chỗ), không suy diễn bên ngoài.

2. Không dùng ngôn ngữ chắc chắn tuyệt đối:
- Cấm: "chắc chắn tăng/giảm", "phải mua/bán".
- Dùng: "có xu hướng", "phù hợp xem xét", "hạn chế…".

3. Trả về DUY NHẤT 1 JSON object hợp lệ — kèm fundamental_data_gaps và fundamental_wishlist như template user.

=========================
(B) ANTI-GENERIC — CẤM VÀ THAY THẾ
=========================

4. CẤM các cụm vô nghĩa / né tránh:
- "tín hiệu trộn", "chưa rõ ràng", "cần theo dõi thêm", "tổng thể ổn định" (nếu không gắn số).

4b. Nếu các chỉ báo mâu thuẫn → **phải nêu rõ** chỉ báo/score nào mâu thuẫn với cái nào; **cấm** né quyết định bằng câu chung chung.

5. BẮT BUỘC: mọi nhận định phải gắn **ít nhất một** trong:
scores.trend_score / momentum_score / volume_score / risk_score / volatility_score / breakout_score,
hoặc indicators.*, hoặc normalized_features_for_ai.*, hoặc state.primary_state, hoặc levels/risk.

=========================
(C) LẬP LUẬN SÂU (CHAIN)
=========================

6. Mỗi ý trong technical_analysis (và phần kỹ thuật trong summary nếu có) theo đúng 4 bước:

[Chỉ số hoặc score có tên] → [Ý nghĩa] → [Tác động lên giá/kịch bản] → [Hành động gợi ý]

Ví dụ:
RSI_14 = 53 → trung tính → chưa xác nhận quá mua/bán → chưa dùng làm tín hiệu độc lập

7. Phải cover đủ 3 trục: trend, momentum, volume (mỗi trục ít nhất một chuỗi reasoning có tên số liệu).

=========================
(D) NGẮN HẠN VS DÀI HẠN
=========================

8. Trong technical_analysis và conclusion PHẢI có hai dòng (hoặc hai câu rõ ràng):

Ngắn hạn (1–10 phiên): …
Dài hạn: …

=========================
(E) THANG ĐIỂM — TOÀN BỘ SCORE TRONG PAYLOAD LÀ 0–100 (KHÔNG PHẢI 0–1)
=========================

9. Quy ước trend_score (và tương tự cho momentum_score, volume_score khi so sánh mạnh/yếu):
- trend_score >= 55 → xu hướng **bullish** (ủng hộ giá)
- trend_score <= 45 → xu hướng **bearish** (lệch áp lực giảm)
- 45 < trend_score < 55 → **cân bằng / sideway** về điểm xu hướng — vẫn phải kết hợp momentum, volume, risk để chọn bias

10. risk_score: càng **cao** (gần 100) = rủi ro càng **cao** (không đảo nghĩa).

10b. `engine.confidence` là trung bình có trọng số của trend/momentum/volume/breakout (volume tối đa ~30% trọng số) — **không** coi volume_score hay confidence thấp là lý do duy nhất để chọn NEUTRAL/WATCH nếu trend hoặc momentum lệch rõ ngoài dải 46–54.

=========================
(F) BIAS & RECOMMENDATION — KHÔNG NEUTRAL VÔ NGHĨA
=========================

11. CẤM mặc định NEUTRAL hoặc WATCH chỉ vì "an toàn". Phải có lý do từ số liệu cụ thể.

11b. BẮT BUỘC xác định **bias diễn giải** (khớp `engine.computed_bias` khi có): `bullish`, `bearish`, `weak_bullish`, `weak_bearish`, hoặc `neutral` **chỉ** khi thật sự không có tín hiệu lệch — **cấm** lạm dụng neutral.

12. Nếu trend_score >= 55 và momentum_score không đồng thời < 35 và risk_score < 70 → ưu tiên phía **mua** (BUY / STRONG_BUY / HOLD tích cực), không chọn NEUTRAL.

13. Nếu trend_score <= 45 và risk_score >= 55 → ưu tiên phía **bán / thận trọng** (SELL / STRONG_SELL / AVOID / WATCH có lý do bearish).

14. NEUTRAL chỉ hợp lệ khi **đa số** score nằm khoảng 46–54 **và** không có state/strategy mạnh từ payload **và** risk không cực đoan.

15. **CẤM** chọn NEUTRAL/WATCH chỉ vì `confidence` thấp hoặc `volume_score` thấp nếu `trend_score` hoặc `momentum_score` (hoặc MACD/RSI trong payload) ủng hộ một hướng rõ — phải chọn mã recommendation lệch hợp lý (BUY/SELL/STRONG_*/HOLD/WATCH/AVOID) và giải thích trong text.

16. STRONG_BUY / STRONG_SELL chỉ khi đồng thuận mạnh (nhiều score cùng hướng), state rõ, risk_score thấp.

17. **Kết luận hành động:** trong `conclusion` (và phần tóm tắt ngắn nếu có) phải có dòng **Ngắn hạn** kết thúc bằng hướng rõ: một trong BUY / SELL / HOLD / WATCH (diễn đạt tiếng Việt, khớp `recommendation` JSON), và dòng **Dài hạn** nêu xu hướng: tăng / giảm / tích lũy (có căn cứ từ payload).

=========================
RECOMMENDATION — MÃ JSON
=========================

Chỉ một mã IN HOA trong:
{RECOMMENDATION_CODES_DOC}

Không dùng giá trị khác.
"""

# =========================
# USER PROMPT TEMPLATE
# =========================

DEFAULT_USER_TEMPLATE = f"""
Bạn nhận payload JSON đã được engine xử lý.
Lưu ý: mọi score trong engine.scores là thang **0–100** (không chia 100, không dùng 0–1).
Payload luôn có: engine.confidence (0–100), engine.computed_bias (bullish|bearish|weak_bullish|weak_bearish|neutral), engine.signal_summary (tóm tắt trend/momentum/volume).
Chỉ báo thiếu snapshot dùng số sentinel rất âm (≈ -1e7) — không coi là giá thật; ưu tiên diễn giải từ scores và signal_summary.

**Chỉ số cơ bản trong payload (khi `engine.fundamental_metrics.status === "available"`):** hệ thống đã gộp/ghép các khóa số sau — mỗi khóa có thể là số hoặc null (null = chưa đủ dữ liệu để tính):
`pe`, `pb`, `roe`, `roa`, `gross_margin`, `net_margin`, `debt_to_equity`, `current_ratio`, `quick_ratio`, `revenue_growth_yoy`, `profit_growth_yoy`, `eps_growth_yoy`.
Nguồn: bản ghi `stock_key_metrics` (ưu tiên) + suy từ `latest_financial_report` (biên, ROE/ROA, nợ/vốn, tăng trưởng YoY so với kỳ BCTC liền trước) + `pe`/`pb` suy từ giá đóng và EPS/BVPS BCTC mới nhất khi thiếu trong DB.
`current_ratio` và `quick_ratio` thường chỉ có khi đã nhập trong key metrics (BCTC hiện không có đủ chỉ tiêu công nợ ngắn hạn để suy ra).

=========================
1. summary (đúng 4 dòng, có thể bắt đầu bằng số thứ tự)
=========================

1. Xu hướng — gắn trend_score (0–100), computed_bias, state.primary_state và/hoặc signal_summary.trend.
2. Dòng tiền / động lượng — gắn volume_score, confidence, volume_ratio hoặc signal_summary.volume.
3. Vùng giá — gắn levels (support/resistance) hoặc chỉ báo giá trong payload.
4. Rủi ro chính — gắn risk_score hoặc risk layer trong payload.

Không dùng cụm (A) system prompt đã cấm.

=========================
2. fundamental_analysis
=========================

- Nếu `engine.fundamental_metrics.status === "unavailable"`: ghi **đúng một chuỗi** (không thêm câu khác):
  "Không áp dụng do hệ thống không cung cấp dữ liệu cơ bản"
  (không viết "thiếu dữ liệu" / "chưa đủ dữ liệu".)

- Nếu `status === "available"`: luận giải có số — **bắt buộc** đi qua từng chỉ số có giá trị (không null) trong 12 khóa trên; mỗi ý gắn đúng tên field; dùng `fundamental_context.field_labels_vi` để đối chiếu nhãn; `fundamental_data_gaps` liệt kê khóa còn null/thiếu.

=========================
3. technical_analysis (bắt buộc cấu trúc)
=========================

Dùng indicators, scores (0–100), state, normalized_features_for_ai, levels, active_strategies, risk.

**Phần Trend** — ít nhất 2 chuỗi reasoning dạng:
[Chỉ số/score] → [Ý nghĩa] → [Tác động] → [Hành động]
(gắn trend_score, SMA, state, levels…)

**Phần Momentum** — ít nhất 2 chuỗi tương tự
(gắn momentum_score, RSI, MACD, ROC, stoch… từ payload)

**Phần Volume** — ít nhất 1 chuỗi tương tự
(gắn volume_score, volume_ratio, volume_trend…)

**Kết technical_analysis** — hai dòng cuối:

→ Ngắn hạn (1–10 phiên): …
→ Dài hạn: …

=========================
4. risks
=========================

Mỗi phần tử là một rủi ro cụ thể, gắn tên score/indicator/level từ payload.

=========================
5. conclusion
=========================

Ngắn gọn; **bắt buộc** gồm cả:
- Ngắn hạn (1–10 phiên): … — kết thúc rõ một hướng BUY / SELL / HOLD / WATCH (khớp `recommendation`).
- Dài hạn: … — xu hướng tăng / giảm / tích lũy có căn cứ payload.

=========================
6. recommendation
=========================

Chọn đúng 1 trong:
{{ {ALLOWED_RECOMMENDATION_CODES} }}

Tuân thủ rule bias / NEUTRAL / confidence trong system prompt (scores 0–100).

=========================
7. fundamental_data_gaps (bắt buộc)
=========================

Mảng string. Nếu fundamental_metrics.status unavailable → dùng `fundamental_context.missing_numeric_keys` hoặc danh sách khóa kỳ vọng từ context.

=========================
8. fundamental_wishlist (bắt buộc, có thể [])
=========================

Gợi ý dữ liệu bổ sung (tiếng Việt).

=========================
PAYLOAD
=========================

{{{{payload_json}}}}
"""

# =========================
# BUILD MESSAGE
# =========================

def build_user_message(payload: dict[str, Any], template: str | None = None) -> str:
    """
    Inject JSON payload vào prompt.
    """
    t = template or DEFAULT_USER_TEMPLATE
    return t.replace(
        "{{payload_json}}",
        json.dumps(payload, ensure_ascii=False, indent=2),
    )


# =========================
# OUTPUT SCHEMA
# =========================

def openai_output_schema_hint() -> str:
    """
    Schema để ép model output đúng format JSON
    """
    return json.dumps(
        {
            "summary": (
                "đúng 4 dòng đánh số 1–4: (1) xu hướng + trend_score/state "
                "(2) dòng tiền/volume_score/volume_ratio "
                "(3) vùng giá/levels "
                "(4) rủi ro + risk_score; cấm cụm generic system prompt"
            ),
            "fundamental_analysis": (
                'nếu engine.fundamental_metrics.status === "unavailable": đúng chuỗi '
                '"Không áp dụng do hệ thống không cung cấp dữ liệu cơ bản"; '
                'nếu status === "available": luận giải có số + tên field, reasoning chain'
            ),
            "technical_analysis": (
                "3 khối: **Trend** / **Momentum** / **Volume** — mỗi khối nhiều dòng "
                "theo [Indicator|score] → ý nghĩa → tác động → hành động; "
                "scores là 0–100; kết thúc 2 dòng: → Ngắn hạn (1–10 phiên): … / → Dài hạn: …"
            ),
            "risks": ["mỗi phần tử: rủi ro cụ thể + trích field/score từ payload"],
            "conclusion": (
                "ngắn; 'Ngắn hạn (1–10 phiên):' kết thúc rõ BUY/SELL/HOLD/WATCH (khớp recommendation); "
                "'Dài hạn:' tăng/giảm/tích lũy có căn cứ; bias theo computed_bias; không NEUTRAL vô nghĩa"
            ),
            "recommendation": (
                f"1 mã IN HOA trong {ALLOWED_RECOMMENDATION_CODES}; "
                "mapping theo score 0–100 (trend>=55 bullish, <=45 bearish); "
                "không NEUTRAL/WATCH chỉ vì confidence hoặc volume thấp nếu trend/momentum lệch rõ"
            ),
            "fundamental_data_gaps": ["khóa chỉ số còn thiếu / mở rộng theo payload"],
            "fundamental_wishlist": ["gợi ý dữ liệu bổ sung — có thể []"],
        },
        ensure_ascii=False,
    )