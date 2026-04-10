# STOCK_ANALYSIS_STRATEGY_ENGINE.md

## 1. Mục tiêu tài liệu

Tài liệu này mô tả **kiến trúc chiến lược phân tích 1 mã chứng khoán** dựa trên dữ liệu **OHLCV time series** để phục vụ cho việc triển khai hệ thống:

- **Backend**: Python + FastAPI
- **Frontend**: NextJS + TypeScript
- **Database**: MySQL

> Mục tiêu của hệ thống **không phải** là quét toàn thị trường,
> mà là **phân tích sâu 1 mã cổ phiếu duy nhất** và đưa ra:
>
> - trạng thái hiện tại của mã
> - tín hiệu chiến lược
> - điểm mạnh / điểm yếu
> - cảnh báo rủi ro
> - phần luận giải AI dễ hiểu cho người dùng

---

# 2. Phạm vi hệ thống

## 2.1 Input dữ liệu

Hệ thống nhận dữ liệu time series theo ngày với cấu trúc tối thiểu:

```json
{
  "date": "2026-04-09",
  "open": 25.1,
  "high": 25.8,
  "low": 24.9,
  "close": 25.4,
  "volume": 3200000
}
```

## 2.2 Output hệ thống

Hệ thống phải trả về:

- Các **chỉ báo kỹ thuật**
- Các **score đánh giá**
- **Trạng thái thị trường** của mã
- **Chiến lược phù hợp hiện tại**
- **Tín hiệu hành động**
- **Hỗ trợ / kháng cự**
- **Luận giải AI**

---

# 3. Triết lý thiết kế

Hệ thống **không nên** chỉ dừng ở việc hiển thị indicator như:

- RSI = 63
- MACD = 1.21
- MA20 = 24.8

Vì như vậy **không hỗ trợ ra quyết định**.

Hệ thống phải đi theo pipeline sau:

```text
OHLCV Data
→ Feature Engineering
→ Scoring Engine
→ Market State Classification
→ Strategy Engine
→ AI Interpretation Layer
```

---

# 4. Kiến trúc tổng thể

Hệ thống được chia thành **6 lớp chính**:

1. **Data Processing Layer**
2. **Feature Engineering Layer**
3. **Scoring Engine**
4. **Market State Classification**
5. **Strategy Engine**
6. **AI Interpretation Layer**

---

# 5. Data Processing Layer

## 5.1 Mục tiêu

Chuẩn hóa dữ liệu đầu vào để đảm bảo tính đúng đắn cho các thuật toán phía sau.

## 5.2 Các bước xử lý

### 5.2.1 Parse và chuẩn hóa dữ liệu

- Convert ngày về `datetime`
- Sort theo thứ tự tăng dần theo ngày
- Convert toàn bộ giá trị số về `float` / `int`
- Loại bỏ record null / lỗi

### 5.2.2 Kiểm tra chất lượng dữ liệu

Kiểm tra các điều kiện:

- `high >= max(open, close, low)`
- `low <= min(open, close, high)`
- `volume >= 0`
- Không có ngày bị trùng

### 5.2.3 Tạo các trường cơ sở

Mỗi record nên có thêm:

- `prev_close`
- `price_change`
- `price_change_pct`

---

# 6. Feature Engineering Layer

## 6.1 Mục tiêu

Chuyển dữ liệu OHLCV thành các **feature có ý nghĩa chiến lược**.

---

# 7. Nhóm Feature A — Price Action Features

## 7.1 Daily Return

```text
daily_return = (close / prev_close) - 1
```

## 7.2 Gap Percent

```text
gap_percent = (open / prev_close) - 1
```

## 7.3 Intraday Range

```text
intraday_range = (high - low) / low
```

## 7.4 Candle Body Size

```text
body_size = abs(close - open)
```

## 7.5 Upper Shadow

```text
upper_shadow = high - max(open, close)
```

## 7.6 Lower Shadow

```text
lower_shadow = min(open, close) - low
```

## 7.7 Close Position in Range

```text
close_position_in_range = (close - low) / (high - low)
```

> Dùng để biết giá đóng gần đỉnh phiên hay gần đáy phiên.

---

# 8. Nhóm Feature B — Trend Features

## 8.1 Moving Averages cần tính

- `sma_5`
- `sma_10`
- `sma_20`
- `sma_50`
- `sma_200`
- `ema_12`
- `ema_26`

## 8.2 Feature suy luận xu hướng

- `close_above_sma20`
- `close_above_sma50`
- `close_above_sma200`
- `sma20_above_sma50`
- `sma50_above_sma200`
- `distance_to_sma20`
- `distance_to_sma50`
- `distance_to_sma200`
- `trend_slope_20`
- `trend_slope_50`

## 8.3 Công thức khoảng cách

```text
distance_to_sma20 = (close - sma_20) / sma_20
```

## 8.4 Công thức slope đơn giản

```text
trend_slope_20 = (sma_20_today - sma_20_5_days_ago) / sma_20_5_days_ago
```

---

# 9. Nhóm Feature C — Momentum Features

## 9.1 Chỉ báo cần tính

- `rsi_14`
- `macd`
- `macd_signal`
- `macd_histogram`
- `stoch_k`
- `stoch_d`
- `roc_10`

## 9.2 Ý nghĩa

- **RSI**: đo sức mạnh tăng / giảm gần đây
- **MACD**: đo động lượng xu hướng
- **Stochastic**: đo trạng thái overbought / oversold ngắn hạn
- **ROC**: đo tốc độ thay đổi giá

---

# 10. Nhóm Feature D — Volume Features

## 10.1 Chỉ số cần tính

- `volume_sma_5`
- `volume_sma_20`
- `volume_ratio`
- `up_volume`
- `down_volume`
- `volume_trend`

## 10.2 Công thức volume ratio

```text
volume_ratio = volume / volume_sma_20
```

## 10.3 Logic cơ bản

- Giá tăng + volume tăng → xác nhận tốt
- Giá tăng + volume yếu → tín hiệu yếu
- Giá giảm + volume lớn → áp lực bán mạnh

---

# 11. Nhóm Feature E — Volatility Features

## 11.1 Chỉ số cần tính

- `atr_14`
- `rolling_std_20`
- `bollinger_upper`
- `bollinger_middle`
- `bollinger_lower`
- `bollinger_width`

## 11.2 Bollinger Width

```text
bollinger_width = (bollinger_upper - bollinger_lower) / bollinger_middle
```

## 11.3 Ý nghĩa

- Width thấp → thị trường đang siết biên
- Width tăng mạnh → biến động đang mở rộng

---

# 12. Nhóm Feature F — Structure Features

## 12.1 Chỉ số cần tính

- `highest_high_20`
- `lowest_low_20`
- `highest_high_50`
- `lowest_low_50`
- `pivot_high`
- `pivot_low`
- `support_zone`
- `resistance_zone`
- `distance_to_breakout`
- `distance_to_support`

## 12.2 Breakout Distance

```text
distance_to_breakout = (highest_high_20 - close) / close
```

## 12.3 Support Distance

```text
distance_to_support = (close - support_zone) / close
```

---

# 13. Scoring Engine

## 13.1 Mục tiêu

Thay vì dùng if-else cứng, hệ thống dùng **score từ 0–100** để đánh giá từng khía cạnh.

Các score cần có:

- `trend_score`
- `momentum_score`
- `volume_score`
- `volatility_score`
- `risk_score`
- `breakout_score`

---

# 14. Trend Score

## 14.1 Mục tiêu

Đánh giá mức độ khỏe của xu hướng.

## 14.2 Gợi ý chấm điểm

- Close > SMA20 → +15
- Close > SMA50 → +10
- SMA20 > SMA50 → +20
- SMA50 > SMA200 → +15
- Slope SMA20 dương → +15
- Slope SMA50 dương → +10
- Giá gần đỉnh 20 phiên → +15

## 14.3 Ngưỡng đánh giá

- `80–100`: Xu hướng rất mạnh
- `60–79`: Xu hướng tích cực
- `40–59`: Trung tính
- `<40`: Xu hướng yếu

---

# 15. Momentum Score

## 15.1 Mục tiêu

Đánh giá sức mạnh động lượng hiện tại.

## 15.2 Gợi ý chấm điểm

- RSI > 55 → +20
- RSI > 60 → +10 thêm
- MACD > Signal → +20
- MACD Histogram dương → +15
- ROC10 dương → +15
- Stochastic K > D → +10
- Giá đóng gần đỉnh phiên → +10

## 15.3 Lưu ý

Momentum cao không luôn đồng nghĩa là “an toàn”, vì có thể đã quá nóng.

---

# 16. Volume Score

## 16.1 Mục tiêu

Đánh giá mức độ xác nhận của dòng tiền.

## 16.2 Gợi ý chấm điểm

- Volume ratio > 1.2 → +20
- Volume ratio > 1.5 → +15 thêm
- Giá tăng kèm volume tăng → +20
- 5 phiên gần nhất volume cải thiện → +15
- Breakout kèm volume → +20

---

# 17. Volatility Score

## 17.1 Mục tiêu

Đánh giá độ phù hợp của biến động đối với chiến lược.

## 17.2 Ý nghĩa

- Volatility quá thấp → khó tạo lợi nhuận
- Volatility quá cao → rủi ro cao

## 17.3 Gợi ý logic

Score càng cao khi:

- ATR ở mức vừa phải
- Bollinger Width mở rộng hợp lý
- Biến động không quá hỗn loạn

---

# 18. Risk Score

## 18.1 Mục tiêu

Đánh giá rủi ro hiện tại của mã.

## 18.2 Gợi ý chấm điểm

Rủi ro tăng khi:

- Close < SMA20
- Close < SMA50
- MACD âm
- RSI < 45
- Volume phân phối lớn
- Thủng hỗ trợ gần
- Drawdown lớn

## 18.3 Ngưỡng gợi ý

- `0–30`: Rủi ro thấp
- `31–60`: Rủi ro trung bình
- `61–100`: Rủi ro cao

---

# 19. Breakout Score

## 19.1 Mục tiêu

Đánh giá khả năng / chất lượng breakout.

## 19.2 Gợi ý chấm điểm

- Close > highest_high_20 → +25
- Volume ratio > 1.5 → +25
- Bollinger squeeze trước đó → +15
- RSI > 60 → +10
- Close near high of day → +10
- Không quá xa hỗ trợ gần → +15

## 19.3 Ngưỡng đánh giá

- `>75`: Breakout mạnh
- `55–75`: Breakout đáng theo dõi
- `<55`: Breakout yếu / dễ false

---

# 20. Market State Classification

## 20.1 Mục tiêu

Xác định mã đang ở **trạng thái nào**.

Hệ thống nên phân loại về **1 trạng thái chính** tại mỗi thời điểm.

---

# 21. Các trạng thái chính

## STATE_1 — Strong Uptrend

### Điều kiện gợi ý

- `trend_score >= 80`
- `momentum_score >= 65`
- `close > sma20 > sma50`
- `risk_score <= 35`

### Ý nghĩa

- Mã đang khỏe
- Ưu tiên chiến lược theo xu hướng hoặc pullback

---

## STATE_2 — Weak Uptrend

### Điều kiện gợi ý

- `trend_score 60–79`
- `momentum_score 50–65`
- Giá vẫn trên MA20 nhưng yếu dần

### Ý nghĩa

- Xu hướng tăng còn nhưng không mạnh
- Có thể rung lắc / test hỗ trợ

---

## STATE_3 — Sideway Accumulation

### Điều kiện gợi ý

- `trend_score trung tính`
- `bollinger_width thấp`
- `atr giảm`
- `distance_to_breakout nhỏ`
- Volume thấp hoặc ổn định

### Ý nghĩa

- Mã đang tích lũy
- Có thể chuẩn bị cho chuyển động lớn

---

## STATE_4 — Breakout Setup

### Điều kiện gợi ý

- Giá tiến sát kháng cự
- `breakout_score >= 60`
- `bollinger_width thấp rồi tăng dần`
- `volume_score khá`

### Ý nghĩa

- Có xác suất cao xảy ra breakout
- Nên theo dõi hành động giá sát sao

---

## STATE_5 — Distribution / Weakening

### Điều kiện gợi ý

- Giá đi ngang sau một nhịp tăng
- Volume cao nhưng không vượt đỉnh
- Momentum suy yếu
- Rủi ro tăng dần

### Ý nghĩa

- Có dấu hiệu phân phối
- Cần thận trọng với tín hiệu mua mới

---

## STATE_6 — Downtrend

### Điều kiện gợi ý

- `trend_score < 40`
- `close < sma20 < sma50`
- `momentum_score thấp`
- `risk_score cao`

### Ý nghĩa

- Mã đang yếu
- Không phù hợp chiến lược mua đuổi

---

## STATE_7 — Oversold Rebound Candidate

### Điều kiện gợi ý

- RSI thấp
- Giảm sâu trước đó
- Xuất hiện nến hồi
- Volume cải thiện nhẹ

### Ý nghĩa

- Có thể hồi kỹ thuật
- Nhưng chưa chắc là đảo chiều xu hướng chính

---

# 22. Strategy Engine

## 22.1 Mục tiêu

Từ **state + score + feature**, hệ thống phải xác định:

- Chiến lược nào đang phù hợp nhất
- Tín hiệu hiện tại là gì
- Mức độ tin cậy bao nhiêu
- Rủi ro nằm ở đâu

Mỗi chiến lược phải có 3 phần:

1. **Entry Logic**
2. **Confidence Score**
3. **Risk Layer**

---

# 23. STRATEGY_1 — Trend Following

## 23.1 Mục tiêu

Đi theo xu hướng tăng đang duy trì.

## 23.2 Áp dụng khi

- `state in [Strong Uptrend, Weak Uptrend]`

## 23.3 Entry Logic

Ví dụ điều kiện:

- `close > sma20 > sma50`
- `rsi_14 > 55`
- `macd > macd_signal`
- `distance_to_sma20` không quá xa

## 23.4 Confidence Score

Chấm dựa trên:

- Trend Score
- Momentum Score
- Volume Score

## 23.5 Risk Layer

Cảnh báo nếu:

- Giá quá xa MA20
- RSI quá nóng
- Volume suy yếu

## 23.6 Output mong muốn

- `signal`: Positive / Watch / Weak
- `confidence`: 0–100
- `reason`: giải thích ngắn

---

# 24. STRATEGY_2 — Pullback Buy

## 24.1 Mục tiêu

Tìm cơ hội khi giá điều chỉnh về hỗ trợ trong xu hướng tăng.

## 24.2 Áp dụng khi

- `state in [Strong Uptrend, Weak Uptrend]`

## 24.3 Entry Logic

Ví dụ điều kiện:

- Giá trên SMA50
- Giá điều chỉnh về gần SMA20 hoặc hỗ trợ gần
- RSI hạ nhiệt nhưng chưa gãy
- Volume giảm khi điều chỉnh

## 24.4 Tư duy chiến lược

Pullback đẹp thường có đặc điểm:

- giá giảm vừa phải
- volume co lại
- không thủng cấu trúc xu hướng

## 24.5 Risk Layer

Cảnh báo nếu:

- Pullback quá sâu
- Thủng MA50
- Volume bán tăng mạnh

---

# 25. STRATEGY_3 — Breakout Detection

## 25.1 Mục tiêu

Phát hiện khi giá phá vỡ vùng tích lũy hoặc kháng cự.

## 25.2 Áp dụng khi

- `state in [Sideway Accumulation, Breakout Setup]`

## 25.3 Entry Logic

Ví dụ điều kiện:

- `close > highest_high_20`
- `volume_ratio > 1.5`
- `bollinger_width` trước đó thấp
- `rsi_14` cải thiện

## 25.4 Kết quả tín hiệu

Hệ thống nên phân biệt:

- `Breakout Confirmed`
- `Breakout Watch`
- `False Breakout Risk`

## 25.5 Risk Layer

Cảnh báo nếu:

- Giá breakout nhưng volume yếu
- Giá đóng không giữ được gần đỉnh phiên
- Breakout quá xa nền tích lũy

---

# 26. STRATEGY_4 — Mean Reversion / Oversold Bounce

## 26.1 Mục tiêu

Tìm nhịp hồi kỹ thuật sau pha giảm mạnh.

## 26.2 Áp dụng khi

- `state == Oversold Rebound Candidate`

## 26.3 Entry Logic

Ví dụ điều kiện:

- RSI thấp trước đó
- Giá chạm hỗ trợ mạnh
- Xuất hiện nến hồi
- Volume hồi xuất hiện

## 26.4 Cảnh báo bắt buộc

Hệ thống phải nhấn mạnh:

> Đây là chiến lược hồi kỹ thuật ngắn hạn,
> chưa phải xác nhận đảo chiều xu hướng chính.

## 26.5 Risk Layer

Cảnh báo nếu:

- Hồi nhưng volume yếu
- Vẫn nằm dưới MA20 / MA50
- Chưa phá cấu trúc giảm

---

# 27. STRATEGY_5 — Risk Warning / Exit Alert

## 27.1 Mục tiêu

Phát hiện khi mã bắt đầu xấu đi hoặc rủi ro tăng cao.

## 27.2 Áp dụng khi

- `state in [Distribution / Weakening, Downtrend]`

## 27.3 Entry Logic

Ví dụ điều kiện:

- Thủng MA20 / MA50
- MACD cắt xuống
- Volume phân phối tăng
- Mất hỗ trợ quan trọng

## 27.4 Kết quả tín hiệu

- `Risk Increasing`
- `Trend Weakening`
- `Support Test Alert`

## 27.5 Risk Layer

Đây là chiến lược cảnh báo nên phải:

- nói rõ vùng invalidation
- nêu vùng hỗ trợ cần quan sát
- không dùng ngôn ngữ quá tuyệt đối kiểu “phải bán”

---

# 28. Chiến lược chấm điểm cho từng strategy

Mỗi strategy nên có cấu trúc output thống nhất:

```json
{
  "name": "Breakout Detection",
  "signal": "Watch Closely",
  "confidence": 76,
  "reason": "Giá đang tiến sát vùng kháng cự 20 phiên, thanh khoản cải thiện và biên độ siết lại.",
  "risk_notes": [
    "Volume vẫn chưa đủ mạnh để xác nhận hoàn toàn breakout",
    "Cần theo dõi phản ứng tại vùng 25.9"
  ]
}
```

---

# 29. Signal Layer

## 29.1 Mục tiêu

Chuẩn hóa tín hiệu để frontend hiển thị thống nhất.

## 29.2 Bộ signal đề xuất

### Tích cực

- `Positive`
- `Strong Positive`
- `Breakout Confirmed`
- `Trend Healthy`

### Trung tính

- `Neutral`
- `Watch`
- `Watch Closely`
- `Accumulating`

### Tiêu cực

- `Weakening`
- `Risk Increasing`
- `Breakdown Risk`
- `Negative`

---

# 30. Support / Resistance Engine

## 30.1 Mục tiêu

Tìm các vùng giá quan trọng để phục vụ:

- chiến lược
- cảnh báo
- AI summary

## 30.2 Output cần có

- `nearest_support`
- `strong_support`
- `nearest_resistance`
- `strong_resistance`

## 30.3 Gợi ý logic

Support / Resistance có thể lấy từ:

- Pivot High / Low
- Highest High / Lowest Low theo cửa sổ 20 / 50 phiên
- Các vùng nhiều lần phản ứng giá

---

# 31. Risk Management Layer

## 31.1 Mục tiêu

Dù hệ thống không đưa lệnh giao dịch trực tiếp, vẫn nên có lớp hỗ trợ quản trị rủi ro.

## 31.2 Các output nên có

- `risk_level`
- `stop_watch_zone`
- `invalidation_zone`
- `drawdown_risk`

## 31.3 Ví dụ ý nghĩa

- `stop_watch_zone`: vùng giá cần theo dõi sát nếu bị xuyên thủng
- `invalidation_zone`: vùng làm suy yếu luận điểm chiến lược hiện tại

---

# 32. AI Interpretation Layer

## 32.1 Mục tiêu

Biến dữ liệu và score thành ngôn ngữ tự nhiên dễ hiểu.

## 32.2 AI không được tự bịa

AI summary chỉ được phép dựa trên:

- state
- score
- support / resistance
- active strategies
- risk layer
- `indicators` (giá trị tuyệt đối trên phiên cuối; xem §32.6 nếu là sentinel)
- `normalized_features_for_ai` (feature đã chuẩn hóa / nhãn — xem §32.5; `null` được thay bằng chuỗi `"unavailable"` trong cây JSON)
- `confidence` (0–100), `computed_bias` (`bullish` | `bearish` | `neutral`), `signal_summary` (tóm tắt trend/momentum/volume — xem §32.6)
- `fundamental_metrics` (luôn là object, không `null` — `status`: `available` | `unavailable`)

## 32.3 Cấu trúc luận giải khuyến nghị

Mỗi summary nên gồm 4 phần:

1. **Xu hướng hiện tại**
2. **Dòng tiền / động lượng**
3. **Vùng quan trọng**
4. **Rủi ro cần lưu ý**

## 32.4 Ví dụ

> Cổ phiếu đang duy trì xu hướng tăng ngắn hạn khi giá tiếp tục nằm trên MA20 và MA50. Động lượng hiện vẫn tích cực, dù đã có dấu hiệu chậm lại sau nhịp tăng gần đây. Thanh khoản duy trì ở mức khá, cho thấy dòng tiền chưa rút ra rõ rệt. Trong ngắn hạn, vùng kháng cự gần cần theo dõi là 25.9, trong khi hỗ trợ gần nằm quanh 24.8. Nếu giá giữ được trên vùng hỗ trợ này, xu hướng tăng vẫn được bảo toàn; ngược lại, rủi ro rung lắc điều chỉnh có thể gia tăng.

## 32.5 Payload bổ sung cho AI — `normalized_features_for_ai`

Mục tiêu: đưa vào prompt các **đại lượng đã tính** từ cùng pipeline Feature Engineering (`features.py`), dạng dễ đọc cho mô hình (phần trăm, 0–1, nhãn rời), **không** thay thế `scores` / `state` / strategy engine.

| Nhóm | Trường chính | Cách tính / ý nghĩa |
|------|----------------|---------------------|
| `price_action` | `daily_return_pct`, `gap_pct` | `daily_return = close/prev_close - 1`, `gap_percent = open/prev_close - 1` (engine §7); nhân 100 → % hiển thị. |
| | `close_position_in_bar_0_to_1` | `(close - low) / (high - low)` — 0 gần đáy nến, 1 gần đỉnh. |
| | `intraday_range_pct` | `(high - low) / low × 100` — biên độ phiên so với đáy. |
| `trend_structure` | `close_above_sma*` / `sma20_above_sma50` … | So sánh boolean từ giá đóng và SMA (engine §8). |
| | `ma_alignment` | `bull_stack` nếu SMA20 > SMA50 > SMA200; `bear_stack` nếu ngược lại; còn lại `mixed`. |
| | `distance_close_to_sma*_pct` | `(close - SMA*) / SMA* × 100` — lệch % so với từng MA. |
| | `sma20_slope_5d_pct`, `sma50_slope_5d_pct` | `(SMA_today - SMA_5_ngày_trước) / SMA_5_ngày_trước × 100`. |
| `momentum` | `rsi_14`, `rsi_zone` | RSI Wilder 14 (§9); zone: `<30` oversold, `30–45` weak_bearish, `45–55` neutral, `55–70` strong_bullish, `≥70` overbought. |
| | `macd_vs_signal_state` | `macd_above_signal` / `macd_below_signal` / `macd_equals_signal` (so khớp EMA12−26 vs signal EMA9). |
| | `macd_signal_cross_hint` | So phiên cuối với phiên liền trước: `bullish_cross` khi MACD vừa vượt signal; `bearish_cross` khi vừa cắt xuống. |
| | `stoch_k`, `stoch_d`, `roc_10_pct` | Stochastic %K/%D (14), ROC 10 phiên % (§9). |
| `volatility` | `atr_pct_of_close` | `ATR14 / close × 100` (ATR Wilder §11). |
| | `bollinger_width_ratio` | `(upper - lower) / middle` (đã là tỷ lệ trên giá mid). |
| | `bollinger_close_position_0_to_1` | `(close - lower) / (upper - lower)` trong dải Bollinger 20, 2σ. |
| | `rolling_std_20_daily_return_stdev_pct` | Độ lệch chuẩn 20 phiên của `daily_return`, ×100 → đơn vị % biến động lợi nhuận ngày. |
| `volume` | `volume_ratio_vs_20d_sma` | `volume / SMA(volume, 20)`. |
| | `volume_trend_5v20` | `SMA(volume,5) - SMA(volume,20)`. |
| `structure_and_risk_proxies` | `distance_to_20d_high_pct` | `(highest_high_20 - close) / close × 100` — còn bao xa đỉnh 20 phiên. |
| | `distance_above_20d_low_pct` | `(close - lowest_low_20) / close × 100`. |
| | `drawdown_from_series_peak_pct` | `(rolling_max(close) - close) / rolling_max(close) × 100` trên toàn chuỗi nhập engine (proxy drawdown). |

Triển khai: `app/modules/indicators/ai_payload_features.py` (`build_normalized_features_for_ai`), sau đó `normalized_features_without_null` trong `engine_completeness.py` thay `null` bằng `"unavailable"` trong cây con.

## 32.6 Độ đầy đủ payload engine (Data completeness)

Mục tiêu: payload gửi AI / API **không chứa `null`** ở các khóa đã cam kết, để model không diễn giải kiểu “thiếu dữ liệu” chung chung.

| Thành phần | Quy ước |
|------------|---------|
| **Sentinel số** | Giá trị `MISSING_INDICATOR_VALUE` ≈ **-9.999.999** trong `indicators.*`, `levels.*`, `risk.stop_watch_zone`, `risk.invalidation_zone` khi không tính được hoặc không có mức giá — **không** là giá thật; MACD/indicator âm hợp lệ vẫn giữ nguyên (chỉ giá trị rất âm cùng mức sentinel mới là thiếu snapshot). |
| **Giá đóng cửa / OHLC** | Luôn số thực từ nến cuối. |
| **`latest_price.change` / `change_pct`** | Nếu thiếu phiên trước → fallback **0.0** (không `null`). |
| **`normalized_features_for_ai`** | `null` trong cây → chuỗi **`"unavailable"`**. |
| **`fundamental_metrics`** | Luôn object: có DB metrics → `{ …fields, "status": "available" }`; không có → `{ "status": "unavailable" }` (sau phân tích đầy đủ, service ghi đè từ pipeline mặc định). |
| **`latest_financial_report`** | Bản ghi BCTC dict hoặc `{ "status": "unavailable" }`. |
| **`confidence`** | Số nguyên **0–100**, từ `calculate_confidence(scores, indicators)` — đồng thuận score kỹ thuật, trừ rủi ro / bất đồng trend–momentum, cộng nhẹ khi nhiều chỉ báo có giá trị hợp lệ. |
| **`computed_bias`** | `trend_score >= 60` → `bullish`; `<= 40` → `bearish`; còn lại → `neutral`. |
| **`signal_summary`** | `{ "trend", "momentum", "volume", "overall_bias" }` — chuỗi tiếng Việt tóm tắt từ scores + chỉ báo (dùng trong prompt). |

Mã nguồn: `app/modules/indicators/engine_completeness.py`; gắn trong `run_indicator_engine` (`pipeline.py`). Phân tích đầy đủ: `analysis_history/service.py` ghi đè `fundamental_metrics` / `latest_financial_report`.

---

# 33. Output JSON chuẩn cho backend

## 33.1 Bổ sung so với mẫu cũ

Các khóa **bắt buộc** thêm (luôn có mặt): `fundamental_metrics`, `confidence`, `computed_bias`, `signal_summary`. `indicators` / `levels` / `risk` dùng số thực; chỗ thiếu dùng sentinel như §32.6 (trong ví dụ dưới vẫn dùng số “đẹp” cho dễ đọc).

Dưới đây là cấu trúc output khuyến nghị cho API.

```json
{
  "symbol": "ABC",
  "analysis_date": "2026-04-09",
  "latest_price": {
    "open": 25.1,
    "high": 25.8,
    "low": 24.9,
    "close": 25.4,
    "volume": 3200000,
    "change": 0.4,
    "change_pct": 1.6
  },
  "indicators": {
    "sma_20": 24.8,
    "sma_50": 23.9,
    "ema_12": 25.0,
    "ema_26": 24.4,
    "rsi_14": 63.4,
    "macd": 0.42,
    "macd_signal": 0.31,
    "macd_histogram": 0.11,
    "atr_14": 0.78,
    "volume_ratio": 1.34,
    "bollinger_width": 0.084
  },
  "normalized_features_for_ai": {
    "as_of": "latest_bar_in_series",
    "price_action": { "daily_return_pct": 0.12, "gap_pct": 0.05, "close_position_in_bar_0_to_1": 0.72, "intraday_range_pct": 3.1 },
    "trend_structure": { "ma_alignment": "bull_stack", "distance_close_to_sma20_pct": 2.4 },
    "momentum": { "rsi_zone": "strong_bullish", "macd_vs_signal_state": "macd_above_signal" },
    "volatility": { "atr_pct_of_close": 3.07 },
    "volume": { "volume_ratio_vs_20d_sma": 1.34 },
    "structure_and_risk_proxies": { "drawdown_from_series_peak_pct": 8.2 }
  },
  "scores": {
    "trend_score": 78,
    "momentum_score": 72,
    "volume_score": 81,
    "volatility_score": 64,
    "risk_score": 44,
    "breakout_score": 76
  },
  "state": {
    "primary_state": "Breakout Setup",
    "description": "Giá đang tiến sát vùng kháng cự sau giai đoạn tích lũy ngắn hạn."
  },
  "levels": {
    "nearest_support": 24.8,
    "strong_support": 24.2,
    "nearest_resistance": 25.9,
    "strong_resistance": 26.4
  },
  "active_strategies": [
    {
      "name": "Breakout Detection",
      "signal": "Watch Closely",
      "confidence": 76,
      "reason": "Giá đang tiến sát vùng kháng cự 20 phiên, thanh khoản cải thiện và biên độ siết lại.",
      "risk_notes": [
        "Volume vẫn chưa đủ mạnh để xác nhận hoàn toàn breakout",
        "Cần theo dõi phản ứng tại vùng 25.9"
      ]
    },
    {
      "name": "Trend Following",
      "signal": "Positive",
      "confidence": 71,
      "reason": "Xu hướng ngắn hạn vẫn duy trì tích cực khi giá nằm trên MA20 và MA50.",
      "risk_notes": [
        "Nếu giá mất MA20, độ mạnh xu hướng sẽ suy giảm"
      ]
    }
  ],
  "risk": {
    "risk_level": "Medium",
    "stop_watch_zone": 24.8,
    "invalidation_zone": 24.2,
    "drawdown_risk": "Moderate"
  },
  "technical_score": 75,
  "fundamental_metrics": {
    "status": "unavailable"
  },
  "confidence": 68,
  "computed_bias": "bullish",
  "signal_summary": {
    "trend": "trend_score=78/100, state=Breakout Setup → Xu hướng nghiêng tích cực theo engine.",
    "momentum": "momentum_score=72/100, RSI_14=63.40, MACD>signal → Động lượng mạnh theo điểm engine.",
    "volume": "volume_score=81/100, volume_ratio=1.34 → Thanh khoản cao / xác nhận tương đối tốt (theo payload).",
    "overall_bias": "bullish"
  },
  "ai_summary": "Cổ phiếu đang trong giai đoạn chuẩn bị breakout sau nhịp tích lũy ngắn hạn..."
}
```

*(Ghi chú: khi chạy phân tích đầy đủ với DB, `fundamental_metrics` có thể là `{ "metric_date": "…", "pe": …, …, "status": "available" }`; `latest_financial_report` tương tự object BCTC hoặc `{ "status": "unavailable" }` — không dùng `null` cho các khóa đó.)*

---

# 34. Thứ tự triển khai khuyến nghị

## Phase 1 — Core Indicator Engine

Làm trước:

- MA / EMA
- RSI
- MACD
- ATR
- Bollinger
- Volume SMA
- Return / Drawdown

## Phase 2 — Scoring Engine

Làm tiếp:

- Trend Score
- Momentum Score
- Volume Score
- Risk Score
- Breakout Score

## Phase 3 — State Classification

Làm tiếp:

- Strong Uptrend
- Weak Uptrend
- Sideway Accumulation
- Breakout Setup
- Distribution / Weakening
- Downtrend
- Oversold Rebound Candidate

## Phase 4 — Strategy Engine

Làm tiếp:

- Trend Following
- Pullback Buy
- Breakout Detection
- Oversold Bounce
- Risk Warning

## Phase 5 — Engine completeness & AI Interpretation

Trước khi gọi LLM:

- Chuẩn hóa payload không `null` (sentinel, `fundamental_metrics.status`, `confidence`, `computed_bias`, `signal_summary`) — §32.6.

Sau đó:

- summary generator
- reason generator
- risk notes generator

---

# 35. Khuyến nghị kỹ thuật khi code

## 35.1 Backend nên tách module rõ ràng

Gợi ý cấu trúc:

```text
app/
  services/
    indicators/
      moving_average.py
      rsi.py
      macd.py
      atr.py
      bollinger.py
    scoring/
      trend_score.py
      momentum_score.py
      volume_score.py
      risk_score.py
      breakout_score.py
    states/
      classifier.py
    strategies/
      trend_following.py
      pullback_buy.py
      breakout_detection.py
      oversold_bounce.py
      risk_warning.py
    interpreters/
      ai_summary_builder.py
```

## 35.2 Nguyên tắc quan trọng

- Không hard-code logic ở 1 file lớn
- Mỗi strategy là 1 module riêng
- Mỗi score là 1 module riêng
- Có thể unit test độc lập từng phần
- Payload engine trước LLM: không để `null` các khóa đã cam kết; sentinel / `fundamental_metrics.status` / `confidence` / `signal_summary` — triển khai thực tế: `app/modules/indicators/engine_completeness.py` + `pipeline.py` (§32.6).

---

# 36. Kết luận

Nếu chỉ phân tích **1 mã chứng khoán**, thì hướng đi đúng nhất là xây:

- **Feature Engine**
- **Scoring Engine**
- **State Engine**
- **Strategy Engine**
- **Interpretation Engine**

> Giá trị thật của sản phẩm không nằm ở việc “hiển thị nhiều indicator”,
> mà nằm ở việc:
>
> **biến dữ liệu giá thành nhận định chiến lược có thể hành động được.**

---

# 37. Hướng mở rộng trong tương lai

Sau khi hoàn thiện engine cơ bản, có thể mở rộng thêm:

- Backtest từng strategy
- Tối ưu ngưỡng score theo lịch sử mã
- Sinh cảnh báo tự động
- Sinh báo cáo ngày / tuần
- AI chat giải thích tín hiệu cho user

---

**End of document**

