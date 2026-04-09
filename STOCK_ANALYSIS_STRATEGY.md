# STOCK_ANALYSIS_STRATEGY.md

# STOCK ANALYSIS PLATFORM — SYSTEM DESIGN & ANALYSIS STRATEGY
## Scope: Vietnamese Stock Market — Start with 1 ticker

---

# 1. MỤC TIÊU TÀI LIỆU

Tài liệu này mô tả:

- Thiết kế hệ thống cho nền tảng phân tích cổ phiếu Việt Nam
- Cách sử dụng dữ liệu lịch sử giá như mẫu user đã cung cấp
- Chiến lược crawl dữ liệu
- Chiến lược tính toán chỉ số
- Chiến lược dùng OpenAI để phân tích
- Các thông tin cần thu thập để đưa ra phân tích đầu tư có giá trị

---

# 2. DỮ LIỆU ĐẦU VÀO USER ĐÃ CUNG CẤP

Ví dụ dữ liệu lịch sử giá của 1 mã cổ phiếu:

```json
{
  "data": [
    {
      "IntDateTime": 0,
      "TradingDate": "/Date(1232643600000)/",
      "LastTradingDate": "/Date(1328688503000)/",
      "Package": 0,
      "OpenIndex": 300.48,
      "HighestIndex": 300.48,
      "LowestIndex": 300.48,
      "CloseIndex": 300.48,
      "Change": 1.99,
      "PerChange": 0.67,
      "TotalVol": 1909141
    },
    {
      "IntDateTime": 0,
      "TradingDate": "/Date(1235667600000)/",
      "LastTradingDate": "/Date(1328688503000)/",
      "Package": 0,
      "OpenIndex": 240.11,
      "HighestIndex": 240.11,
      "LowestIndex": 240.11,
      "CloseIndex": 240.11,
      "Change": 3.20,
      "PerChange": 1.35,
      "TotalVol": 5219460
    }
  ]
}
```

---

# 3. NHẬN ĐỊNH VỀ DỮ LIỆU MẪU

Từ dữ liệu này, hệ thống có thể xác định đây là **historical market price data**.

## 3.1 Ý nghĩa các field

| Field | Ý nghĩa |
|---|---|
| `TradingDate` | Ngày giao dịch |
| `OpenIndex` | Giá mở cửa |
| `HighestIndex` | Giá cao nhất |
| `LowestIndex` | Giá thấp nhất |
| `CloseIndex` | Giá đóng cửa |
| `Change` | Mức thay đổi giá |
| `PerChange` | % thay đổi |
| `TotalVol` | Khối lượng giao dịch |
| `LastTradingDate` | Thời gian cập nhật cuối |
| `Package` | Có thể là package/source-specific field |
| `IntDateTime` | Field nội bộ hoặc không cần dùng trực tiếp |

## 3.2 Kết luận
Từ bộ dữ liệu này, hệ thống có thể xây dựng:

- biểu đồ giá lịch sử
- chỉ báo kỹ thuật
- xu hướng giá
- phân tích volume
- tín hiệu breakout / breakdown
- hành vi giao dịch theo thời gian

Tuy nhiên, **chỉ với dữ liệu giá thì chưa đủ để phân tích đầu tư hoàn chỉnh**.

Muốn phân tích tốt, hệ thống cần thêm các lớp dữ liệu khác.

---

# 4. NHỮNG THÔNG TIN CẦN THU THẬP ĐỂ PHÂN TÍCH CỔ PHIẾU

Đây là phần cực kỳ quan trọng.

Phân tích cổ phiếu tốt không thể chỉ dựa vào giá.

Hệ thống nên phân tích dựa trên **5 lớp dữ liệu chính**:

---

# 5. LỚP DỮ LIỆU 1 — PRICE / MARKET DATA

## 5.1 Mục đích
Dùng để phân tích hành vi giá và xu hướng thị trường.

## 5.2 Dữ liệu cần có
- Open
- High
- Low
- Close
- Volume
- % Change
- Trading Value
- Market Cap (nếu có)
- Shares Outstanding (nếu có)

## 5.3 Dùng để phân tích gì?
- xu hướng tăng / giảm
- sideway
- breakout / breakdown
- biến động mạnh
- volume bất thường
- tín hiệu kỹ thuật

## 5.4 Chỉ số có thể tính
- SMA
- EMA
- RSI
- MACD
- Bollinger Bands
- ATR
- OBV
- Volume MA
- Drawdown
- Volatility

---

# 6. LỚP DỮ LIỆU 2 — FUNDAMENTAL DATA

## 6.1 Mục đích
Dùng để đánh giá chất lượng doanh nghiệp.

## 6.2 Dữ liệu cần crawl / thu thập
- Revenue
- Gross Profit
- Operating Profit
- Net Profit
- EPS
- BVPS
- Total Assets
- Total Liabilities
- Equity
- Cash Flow
- Shares Outstanding

## 6.3 Dùng để phân tích gì?
- doanh nghiệp có tăng trưởng không?
- lợi nhuận có bền không?
- công ty có vay nợ quá cao không?
- hiệu quả kinh doanh có tốt không?

## 6.4 Chỉ số cần tính
- P/E
- P/B
- ROE
- ROA
- Gross Margin
- Net Margin
- Debt/Equity
- Current Ratio
- Quick Ratio
- Revenue Growth YoY
- Profit Growth YoY
- EPS Growth

---

# 7. LỚP DỮ LIỆU 3 — BUSINESS / COMPANY PROFILE

## 7.1 Mục đích
Hiểu doanh nghiệp đang làm gì và nó thuộc loại cổ phiếu nào.

## 7.2 Dữ liệu cần có
- Ticker
- Company Name
- Exchange
- Sector
- Industry
- Business Description
- Market Cap
- Free Float (nếu có)
- Ownership structure (phase 2)

## 7.3 Dùng để phân tích gì?
- doanh nghiệp thuộc nhóm ngành nào?
- có tính chu kỳ hay phòng thủ?
- có phù hợp đầu tư dài hạn hay không?
- định giá hiện tại có hợp lý so với ngành không?

---

# 8. LỚP DỮ LIỆU 4 — NEWS / EVENT DATA

## 8.1 Mục đích
Dùng để hiểu bối cảnh ảnh hưởng đến giá cổ phiếu.

## 8.2 Dữ liệu cần có
- Tin doanh nghiệp
- Tin ngành
- Cổ tức
- Chia tách
- Phát hành thêm
- M&A
- Ban lãnh đạo thay đổi
- KQKD mới công bố
- Giao dịch nội bộ

## 8.3 Dùng để phân tích gì?
- vì sao giá tăng / giảm?
- tăng do tin tốt hay đầu cơ?
- doanh nghiệp có catalyst hay rủi ro gần hạn không?

## 8.4 Gợi ý sử dụng
Dùng OpenAI để:
- tóm tắt tin tức
- gom nhóm sự kiện
- xác định sentiment sơ bộ

---

# 9. LỚP DỮ LIỆU 5 — INTERNAL ANALYSIS SNAPSHOT

## 9.1 Mục đích
Lưu lại “ảnh chụp” trạng thái cổ phiếu tại thời điểm user phân tích.

## 9.2 Cần lưu
- Giá hiện tại
- Các chỉ số cơ bản
- Các chỉ báo kỹ thuật
- Các score nội bộ
- Kết quả AI
- Recommendation

## 9.3 Tại sao quan trọng?
- xem lịch sử thay đổi
- tránh phải gọi AI lại
- giúp người dùng so sánh theo thời gian

---

# 10. CHIẾN LƯỢC PHÂN TÍCH TỔNG THỂ

Hệ thống nên phân tích cổ phiếu theo pipeline sau:

## Bước 1 — Thu thập dữ liệu
- crawl historical prices
- crawl financial reports
- crawl key metrics
- crawl company profile
- crawl news/events

## Bước 2 — Chuẩn hóa dữ liệu
- parse ngày tháng
- parse số
- chuẩn hóa dữ liệu thiếu
- map field từ các nguồn khác nhau

## Bước 3 — Tính toán chỉ số
- technical indicators
- fundamental metrics
- growth metrics
- volatility metrics

## Bước 4 — Chấm điểm nội bộ
- fundamental score
- technical score
- risk score

## Bước 5 — OpenAI phân tích
- đọc toàn bộ dữ liệu đã tính
- viết báo cáo dễ hiểu cho user

## Bước 6 — Lưu lịch sử
- lưu kết quả phân tích vào DB

---

# 11. CHIẾN LƯỢC PHÂN TÍCH THEO 3 GÓC NHÌN

Hệ thống nên đưa ra phân tích dựa trên 3 lớp logic chính:

---

# 12. GÓC NHÌN 1 — FUNDAMENTAL ANALYSIS

## 12.1 Mục tiêu
Trả lời câu hỏi:

> “Doanh nghiệp này có đáng đầu tư dài hạn không?”

## 12.2 Những gì cần xem
- tăng trưởng doanh thu
- tăng trưởng lợi nhuận
- biên lợi nhuận
- ROE / ROA
- nợ
- định giá

## 12.3 Hệ thống nên đánh giá
### Mạnh nếu:
- doanh thu tăng đều
- lợi nhuận tăng đều
- ROE tốt
- nợ hợp lý
- định giá không quá đắt

### Yếu nếu:
- doanh thu đi ngang / giảm
- lợi nhuận không ổn định
- nợ cao
- định giá quá cao
- dòng tiền yếu

## 12.4 Output nên có
- Fundamental Score
- nhận định tăng trưởng
- nhận định sức khỏe tài chính
- nhận định định giá

---

# 13. GÓC NHÌN 2 — TECHNICAL ANALYSIS

## 13.1 Mục tiêu
Trả lời câu hỏi:

> “Điểm vào hiện tại có đẹp hay không?”

## 13.2 Những gì cần xem
- xu hướng MA
- RSI
- MACD
- Bollinger
- ATR
- khối lượng
- breakout / support / resistance

## 13.3 Hệ thống nên đánh giá
### Tích cực nếu:
- giá trên MA20 / MA50 / MA200
- RSI khỏe nhưng chưa quá mua
- MACD bullish
- volume tăng khi breakout

### Tiêu cực nếu:
- giá thủng hỗ trợ
- RSI yếu
- MACD bearish
- volume giảm trong nhịp tăng

## 13.4 Output nên có
- Technical Score
- trend direction
- support/resistance
- entry zone / watch zone / avoid zone

---

# 14. GÓC NHÌN 3 — RISK ANALYSIS

## 14.1 Mục tiêu
Trả lời câu hỏi:

> “Rủi ro của cổ phiếu này là gì?”

## 14.2 Dữ liệu cần xem
- volatility
- drawdown
- debt
- earnings instability
- định giá quá cao
- event risk

## 14.3 Output nên có
- Risk Score
- Top 3–5 risks
- mức độ phù hợp với:
  - nhà đầu tư ngắn hạn
  - nhà đầu tư dài hạn
  - nhà đầu tư thận trọng

---

# 15. CHIẾN LƯỢC CHẤM ĐIỂM NỘI BỘ

Hệ thống nên có cơ chế chấm điểm rõ ràng để AI dựa vào đó diễn giải.

---

# 16. FUNDAMENTAL SCORE (0–100)

## Gợi ý cấu phần
- Revenue Growth: 15 điểm
- Profit Growth: 20 điểm
- ROE: 20 điểm
- Debt/Equity: 15 điểm
- Margin Quality: 15 điểm
- Valuation (P/E, P/B): 15 điểm

## Ý nghĩa
- `80–100`: Rất tốt
- `60–79`: Khá tốt
- `40–59`: Trung bình
- `<40`: Yếu

---

# 17. TECHNICAL SCORE (0–100)

## Gợi ý cấu phần
- Trend Alignment (MA): 25 điểm
- RSI: 15 điểm
- MACD: 20 điểm
- Volume Confirmation: 20 điểm
- Breakout / Support Logic: 20 điểm

## Ý nghĩa
- `80–100`: Tín hiệu kỹ thuật mạnh
- `60–79`: Tương đối tích cực
- `40–59`: Trung tính
- `<40`: Yếu

---

# 18. RISK SCORE (0–100)

## Lưu ý
Ở đây nên hiểu là:

- điểm càng cao = rủi ro càng cao
- hoặc đổi sang “Safety Score” để dễ hiểu hơn

## Gợi ý cấu phần
- Volatility: 25 điểm
- Debt Risk: 20 điểm
- Earnings Instability: 20 điểm
- Drawdown History: 20 điểm
- Event Risk: 15 điểm

---

# 19. KẾT LUẬN TỔNG HỢP

Sau khi có 3 score trên, hệ thống có thể tạo ra recommendation logic.

## Ví dụ rule-based sơ bộ

### BUY
Nếu:
- Fundamental Score >= 75
- Technical Score >= 70
- Risk Score <= 40

### WATCH
Nếu:
- Fundamental tốt nhưng kỹ thuật chưa đẹp
hoặc
- kỹ thuật đẹp nhưng định giá chưa hấp dẫn

### HOLD
Nếu:
- cổ phiếu ổn nhưng không có điểm mua mới rõ ràng

### AVOID
Nếu:
- yếu cả fundamental và technical
hoặc
- risk quá cao

---

# 20. OPENAI SẼ PHÂN TÍCH DỰA TRÊN NHỮNG GÌ?

OpenAI không nên “đoán”.

OpenAI phải đọc **input đã được hệ thống xử lý sẵn**.

---

# 21. INPUT DÀNH CHO OPENAI

Mỗi lần user bấm “Phân tích”, backend sẽ gửi cho OpenAI một payload có cấu trúc như sau:

```json
{
  "ticker": "FPT",
  "company": {
    "name": "FPT Corporation",
    "sector": "Technology",
    "exchange": "HOSE"
  },
  "market_data": {
    "current_price": 123.4,
    "price_change_percent": 1.5,
    "volume": 5200000,
    "trend_summary": "price above MA20 and MA50"
  },
  "fundamental_metrics": {
    "pe": 18.2,
    "pb": 4.1,
    "roe": 22.5,
    "roa": 10.1,
    "revenue_growth_yoy": 13.2,
    "profit_growth_yoy": 15.8,
    "debt_to_equity": 0.45
  },
  "technical_indicators": {
    "rsi_14": 61.4,
    "macd": 1.25,
    "macd_signal": 0.98,
    "sma_20": 118.2,
    "sma_50": 114.7,
    "sma_200": 103.5,
    "bollinger_position": "near upper band"
  },
  "scores": {
    "fundamental_score": 82,
    "technical_score": 74,
    "risk_score": 36
  },
  "news_summary": [
    "Quarterly earnings beat expectations",
    "New strategic partnership announced"
  ]
}
```

---

# 22. OPENAI PHẢI TRẢ RA GÌ?

OpenAI phải trả về JSON có cấu trúc rõ ràng:

```json
{
  "summary": "...",
  "fundamental_analysis": "...",
  "technical_analysis": "...",
  "risks": [
    "...",
    "..."
  ],
  "conclusion": "...",
  "recommendation": "WATCH"
}
```

---

# 23. CHIẾN LƯỢC PROMPT CHO OPENAI

AI phải được ép vai trò rõ ràng:

## Vai trò đề xuất
> “Bạn là chuyên gia phân tích cổ phiếu Việt Nam. Hãy phân tích dữ liệu đã được tính sẵn. Không bịa số liệu. Không khuyến nghị chắc chắn. Chỉ đánh giá dựa trên dữ liệu được cung cấp.”

## Nguyên tắc prompt
- không cho AI tự phát minh số liệu
- không cho AI đưa lời khuyên tài chính tuyệt đối
- bắt AI phân tích theo cấu trúc
- bắt AI giải thích bằng ngôn ngữ dễ hiểu

---

# 24. THIẾT KẾ HỆ THỐNG KỸ THUẬT

---

# 25. STACK CÔNG NGHỆ

## Backend
- Python
- FastAPI

## Frontend
- TypeScript
- Next.js

## Database
- MySQL

## Deployment
- Docker
- Docker Compose

## AI
- OpenAI API

## Optional / Recommended
- Redis (cache / queue sau này)
- Celery hoặc APScheduler cho background jobs

---

# 26. KIẾN TRÚC TỔNG THỂ

```text
[ Next.js Frontend ]
          |
          v
[ FastAPI Backend ]
          |
          +--> [ MySQL ]
          |
          +--> [ OpenAI API ]
          |
          +--> [ Crawler / Worker / Scheduler ]
```

---

# 27. THÀNH PHẦN BACKEND

## 27.1 Auth Module
- đăng ký
- đăng nhập
- phân quyền

## 27.2 Stock Module
- danh sách mã
- chi tiết mã

## 27.3 Crawler Module
- crawl historical prices
- crawl financial reports
- crawl metrics
- crawl company info
- crawl news

## 27.4 Indicator Engine
- tính chỉ số kỹ thuật
- tính chỉ số cơ bản
- tính score

## 27.5 AI Analysis Module
- build prompt
- gọi OpenAI
- parse JSON response

## 27.6 History Module
- lưu lịch sử phân tích

## 27.7 Admin Module
- quản lý user
- quản lý mã
- trigger crawl
- xem logs

---

# 28. CHỨC NĂNG USER

User có thể:

- tạo tài khoản
- đăng nhập
- xem danh sách mã
- chọn mã cổ phiếu
- xem biểu đồ và chỉ số
- bấm “Phân tích”
- xem báo cáo AI
- lưu lịch sử
- xem lại lịch sử

---

# 29. CHỨC NĂNG ADMIN

Admin có thể:

- quản lý users
- quản lý stock tickers
- quản lý lịch sử phân tích
- trigger crawl thủ công
- xem trạng thái crawl
- xem logs
- cấu hình prompt AI

---

# 30. THIẾT KẾ DATABASE TỐI THIỂU

---

# 31. BẢNG users

```sql
users
- id
- full_name
- email
- password_hash
- role
- status
- created_at
- updated_at
```

---

# 32. BẢNG stocks

```sql
stocks
- id
- ticker
- company_name
- exchange
- sector
- description
- is_active
- created_at
- updated_at
```

---

# 33. BẢNG stock_price_histories

## Bảng này map trực tiếp từ dữ liệu user cung cấp

```sql
stock_price_histories
- id
- stock_id
- trading_date
- open_price
- high_price
- low_price
- close_price
- price_change
- percent_change
- total_volume
- raw_payload_json
- created_at
```

## Mapping từ JSON
- `TradingDate` -> `trading_date`
- `OpenIndex` -> `open_price`
- `HighestIndex` -> `high_price`
- `LowestIndex` -> `low_price`
- `CloseIndex` -> `close_price`
- `Change` -> `price_change`
- `PerChange` -> `percent_change`
- `TotalVol` -> `total_volume`

---

# 34. BẢNG stock_financial_reports

```sql
stock_financial_reports
- id
- stock_id
- report_type
- fiscal_year
- fiscal_quarter
- revenue
- gross_profit
- operating_profit
- net_profit
- eps
- bvps
- total_assets
- total_liabilities
- equity
- operating_cash_flow
- free_cash_flow
- raw_payload_json
- created_at
```

---

# 35. BẢNG stock_key_metrics

```sql
stock_key_metrics
- id
- stock_id
- metric_date
- pe
- pb
- roe
- roa
- gross_margin
- net_margin
- debt_to_equity
- current_ratio
- quick_ratio
- revenue_growth_yoy
- profit_growth_yoy
- eps_growth_yoy
- created_at
```

---

# 36. BẢNG stock_technical_indicators

```sql
stock_technical_indicators
- id
- stock_id
- indicator_date
- sma_20
- sma_50
- sma_200
- ema_12
- ema_26
- macd
- macd_signal
- macd_histogram
- rsi_14
- bollinger_upper
- bollinger_middle
- bollinger_lower
- atr_14
- obv
- volume_ma_20
- drawdown_52w
- volatility_30d
- created_at
```

---

# 37. BẢNG analysis_requests

```sql
analysis_requests
- id
- user_id
- stock_id
- request_type
- status
- created_at
- updated_at
```

---

# 38. BẢNG analysis_results

```sql
analysis_results
- id
- analysis_request_id
- user_id
- stock_id
- analysis_date
- snapshot_price
- snapshot_volume
- snapshot_pe
- snapshot_pb
- snapshot_roe
- snapshot_rsi
- snapshot_macd
- fundamental_score
- technical_score
- risk_score
- ai_summary
- ai_fundamental_analysis
- ai_technical_analysis
- ai_risks_json
- ai_conclusion
- ai_recommendation
- raw_ai_response_json
- created_at
```

---

# 39. BẢNG crawl_logs

```sql
crawl_logs
- id
- stock_id
- crawl_type
- status
- message
- started_at
- finished_at
- created_at
```

---

# 40. BẢNG ai_prompt_configs

```sql
ai_prompt_configs
- id
- name
- prompt_type
- system_prompt
- user_prompt_template
- is_active
- version
- created_at
- updated_at
```

---

# 41. API CHÍNH CẦN CÓ

## Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

## Stocks
- `GET /api/stocks`
- `GET /api/stocks/{ticker}`
- `GET /api/stocks/{ticker}/prices`
- `GET /api/stocks/{ticker}/metrics`
- `GET /api/stocks/{ticker}/technicals`

## Analysis
- `POST /api/analysis/{ticker}`
- `GET /api/analysis/history`
- `GET /api/analysis/history/{id}`

## Admin
- `GET /api/admin/users`
- `GET /api/admin/stocks`
- `POST /api/admin/crawl/{ticker}`
- `GET /api/admin/crawl/logs`
- `GET /api/admin/analysis`

---

# 42. QUY TRÌNH PHÂN TÍCH THỰC TẾ

Khi user bấm “Phân tích”, hệ thống nên chạy như sau:

## Step 1
Lấy dữ liệu mới nhất của mã cổ phiếu từ DB

## Step 2
Lấy historical price data để tính:
- RSI
- MACD
- MA
- Bollinger
- volume trends

## Step 3
Lấy financial reports để tính:
- tăng trưởng
- định giá
- lợi nhuận
- chất lượng tài chính

## Step 4
Tính:
- Fundamental Score
- Technical Score
- Risk Score

## Step 5
Tạo JSON input gửi OpenAI

## Step 6
Nhận JSON output từ OpenAI

## Step 7
Lưu analysis result vào DB

## Step 8
Trả kết quả cho frontend

---

# 43. KẾ HOẠCH TRIỂN KHAI THỰC TẾ

---

# 44. GIAI ĐOẠN 1 — FOUNDATION
## Làm gì
- setup repo
- setup docker
- setup FastAPI
- setup Next.js
- setup MySQL
- setup auth

## Output
- hệ thống chạy local

---

# 45. GIAI ĐOẠN 2 — STOCK DATA PIPELINE
## Làm gì
- build crawler cho historical prices
- parse dữ liệu mẫu như user đã cung cấp
- lưu vào `stock_price_histories`

## Output
- lưu được dữ liệu giá lịch sử cho 1 mã

---

# 46. GIAI ĐOẠN 3 — INDICATOR ENGINE
## Làm gì
- build technical calculations
- build fundamental calculations
- build scoring logic

## Output
- hệ thống tính được chỉ số

---

# 47. GIAI ĐOẠN 4 — AI ANALYSIS
## Làm gì
- build prompt
- integrate OpenAI
- parse JSON output
- save analysis history

## Output
- user nhận được báo cáo AI

---

# 48. GIAI ĐOẠN 5 — ADMIN + USER DASHBOARD
## Làm gì
- admin pages
- stock detail page
- analysis history page

## Output
- có thể dùng được end-to-end

---

# 49. KẾT LUẬN CHIẾN LƯỢC QUAN TRỌNG NHẤT

Nếu muốn hệ thống phân tích cổ phiếu có chất lượng thực sự, cần nhớ:

## Không đủ nếu chỉ có:
- giá
- volume
- AI

## Phải có đủ:
1. **Price data**
2. **Financial data**
3. **Business profile**
4. **News / events**
5. **Internal scoring**
6. **AI explanation**

---

# 50. THỨ TỰ LÀM ĐÚNG NHẤT

Đây là thứ tự nên triển khai:

1. **Crawl dữ liệu giá từ JSON mẫu**
2. **Thiết kế bảng DB chuẩn**
3. **Tính technical indicators**
4. **Thêm financial data**
5. **Tính fundamental metrics**
6. **Build scoring engine**
7. **Tích hợp OpenAI**
8. **Xây UI + history + admin**

---

# 51. MVP THỰC CHIẾN NÊN CHỐT

Để ra sản phẩm nhanh nhưng có giá trị, MVP nên là:

- 1 mã cổ phiếu đầu tiên (khuyên: `FPT`)
- crawl dữ liệu lịch sử giá
- tính:
  - SMA
  - EMA
  - RSI
  - MACD
  - Bollinger
  - P/E
  - P/B
  - ROE
  - Revenue Growth
  - Profit Growth
- AI phân tích
- lưu lịch sử
- admin quản lý user / mã / crawl / analysis

---

# 52. KẾT LUẬN CUỐI

Đây là một hệ thống có thể phát triển thành:

- nền tảng phân tích cổ phiếu
- công cụ hỗ trợ quyết định đầu tư
- sản phẩm SaaS tài chính
- hệ thống phân tích nội bộ cho doanh nghiệp

Muốn sản phẩm mạnh và dùng được thật, cần đi theo nguyên tắc:

> **Data trước → Calculation sau → AI cuối cùng**

AI chỉ nên là lớp **giải thích thông minh**, không phải lớp **thay thế hệ thống phân tích**.
