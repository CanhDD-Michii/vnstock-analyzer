# CODE_RULES_BE_FE.md

# CODE RULES — BACKEND & FRONTEND
## Project: Stock Analysis Platform (Vietnam Market)

> Công nghệ cố định:
>
> - **Backend:** Python, FastAPI
> - **Frontend:** TypeScript, Next.js
> - **Database:** MySQL
> - **Deploy:** Docker, Docker Compose

---

# 1. MỤC TIÊU TÀI LIỆU

Tài liệu này định nghĩa **coding rules / engineering rules** cho toàn bộ dự án nhằm đảm bảo:

- code dễ đọc
- dễ maintain
- dễ mở rộng
- dễ review
- dễ test
- tránh viết code “chạy được nhưng rối”
- đồng bộ giữa BE và FE

---

# 2. NGUYÊN TẮC CHUNG TOÀN DỰ ÁN

## 2.1 Ưu tiên
Thứ tự ưu tiên khi viết code:

1. **Correctness**
2. **Readability**
3. **Maintainability**
4. **Scalability**
5. **Performance**
6. **Cleverness (không quan trọng)**

> Không được viết code “thông minh quá mức” làm team khác khó hiểu.

---

## 2.2 Rule quan trọng nhất
### Code phải:
- dễ đọc
- dễ đoán
- ít side effect
- có cấu trúc rõ ràng
- có tên rõ nghĩa

### Code không được:
- nhét toàn bộ logic vào 1 file / 1 function
- viết tắt khó hiểu
- lặp code không kiểm soát
- trộn business logic với transport logic
- trộn UI với data-fetching logic bừa bãi

---

## 2.3 Clean Architecture mindset
Không cần làm architecture quá hàn lâm, nhưng phải tách rõ:

- **presentation**
- **application**
- **domain/business logic**
- **data access / infrastructure**

---

# 3. NAMING RULES (ÁP DỤNG CẢ BE & FE)

## 3.1 Biến / hàm / class phải rõ nghĩa

### Tốt
- `calculateTechnicalIndicators`
- `buildStockAnalysisPrompt`
- `fetchHistoricalPrices`
- `createAnalysisHistory`
- `normalizedVolume`

### Xấu
- `handleData`
- `doStuff`
- `temp`
- `x`
- `abc`
- `runAll`

---

## 3.2 Tên phải phản ánh đúng hành vi

### Không tốt
```ts
saveUser()
```

Nếu thực tế hàm này vừa:
- validate
- hash password
- insert DB
- gửi mail

thì tên này là **quá mơ hồ**.

### Nên
- `registerUser`
- `createUserRecord`
- `hashPassword`
- `sendWelcomeEmail`

---

## 3.3 Quy ước đặt tên

### Backend Python
- file: `snake_case`
- variable: `snake_case`
- function: `snake_case`
- class: `PascalCase`
- constant: `UPPER_SNAKE_CASE`

### Frontend TypeScript / Next.js
- file component: `PascalCase.tsx`
- hooks: `useSomething.ts`
- utils: `camelCase.ts` hoặc `kebab-case.ts` nhưng phải thống nhất
- variable: `camelCase`
- function: `camelCase`
- type/interface: `PascalCase`
- constant: `UPPER_SNAKE_CASE`

---

# 4. BACKEND RULES — PYTHON + FASTAPI

---

# 5. BACKEND KIẾN TRÚC BẮT BUỘC

## 5.1 Không được viết kiểu “route làm hết”

### Sai
Route:
- validate input
- query DB
- tính toán chỉ số
- gọi OpenAI
- build response
- log lỗi

=> tất cả trong 1 file endpoint

### Đúng
Tách thành:

- `router` → nhận request / trả response
- `service` → business logic
- `repository` → query DB
- `schema` → request/response validation
- `utils` → helper thuần
- `domain logic` → calculation / AI prompt / scoring

---

# 6. BACKEND FOLDER RULES

## 6.1 Cấu trúc khuyến nghị

```text
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── stocks.py
│   │   │   ├── analysis.py
│   │   │   └── admin.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── db/
│   │   ├── session.py
│   │   ├── base.py
│   │   └── models/
│   ├── modules/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── stocks/
│   │   ├── crawler/
│   │   ├── indicators/
│   │   ├── ai_analysis/
│   │   ├── analysis_history/
│   │   └── admin/
│   ├── shared/
│   │   ├── schemas/
│   │   ├── enums/
│   │   ├── constants/
│   │   └── utils/
│   └── main.py
├── tests/
└── requirements.txt
```

---

# 7. BACKEND MODULE RULES

Mỗi module nên có cấu trúc tương tự:

```text
modules/stocks/
├── schemas.py
├── service.py
├── repository.py
├── constants.py
├── exceptions.py
└── mapper.py
```

## Ý nghĩa
- `schemas.py` → request/response DTO
- `service.py` → business logic
- `repository.py` → truy vấn DB
- `constants.py` → hằng số module
- `exceptions.py` → custom errors
- `mapper.py` → map DB → response

---

# 8. BACKEND API RULES

## 8.1 Router chỉ làm 4 việc
Router chỉ được:

1. nhận request
2. validate input
3. gọi service
4. trả response

## 8.2 Router không được:
- viết query SQL
- tính RSI / MACD
- viết prompt OpenAI
- parse raw payload phức tạp

---

# 9. BACKEND SERVICE RULES

## 9.1 Service là nơi chứa business logic
Ví dụ:
- phân tích mã chứng khoán
- tính điểm đầu tư
- validate logic nghiệp vụ
- orchestration nhiều repository

## 9.2 Service không nên:
- return raw SQL rows
- phụ thuộc trực tiếp vào framework response
- chứa code format HTTP response

---

# 10. BACKEND REPOSITORY RULES

## 10.1 Repository chỉ lo data access
Repository được phép:
- query DB
- insert / update / delete
- pagination query
- aggregate query

Repository không nên:
- chứa business rules
- chứa AI logic
- chứa technical indicator logic

---

# 11. BACKEND SCHEMA RULES (PYDANTIC)

## 11.1 Bắt buộc dùng schema rõ ràng cho:
- request body
- query params
- response body

## 11.2 Không được:
- trả raw ORM model trực tiếp ra API
- trả field thừa / nhạy cảm

### Sai
```python
return user
```

### Đúng
```python
return UserResponse.model_validate(user)
```

---

# 12. BACKEND MODEL RULES

## 12.1 ORM model chỉ đại diện cho database
ORM model không nên:
- chứa logic AI
- chứa logic business lớn
- chứa quá nhiều helper khó test

## 12.2 Model phải có:
- `id`
- timestamps hợp lý
- index cần thiết
- foreign key rõ ràng

---

# 13. BACKEND FUNCTION RULES

## 13.1 Một function chỉ nên có 1 trách nhiệm chính

### Sai
```python
def analyze_stock():
    # fetch db
    # calculate indicators
    # call openai
    # save history
    # build response
```

### Đúng
```python
def analyze_stock():
    market_snapshot = build_market_snapshot(...)
    scores = calculate_scores(...)
    ai_result = generate_ai_analysis(...)
    return save_analysis_result(...)
```

---

## 13.2 Function quá dài phải tách
### Rule
Nếu function:
- trên ~40–60 dòng
- có nhiều `if/else`
- có nhiều block comment
- có nhiều responsibility

=> **phải xem xét tách**

---

# 14. BACKEND ERROR HANDLING RULES

## 14.1 Không được `except Exception` rồi nuốt lỗi bừa bãi

### Sai
```python
try:
    ...
except Exception:
    return None
```

### Đúng
- log lỗi rõ ràng
- raise custom exception phù hợp
- trả mã lỗi có nghĩa

---

## 14.2 Custom exception phải có ý nghĩa
Ví dụ:
- `StockNotFoundError`
- `AnalysisNotReadyError`
- `InvalidFinancialDataError`
- `OpenAIResponseFormatError`

---

# 15. BACKEND LOGGING RULES

## 15.1 Phải log các điểm quan trọng
Cần log:
- login thất bại
- crawl start / success / fail
- AI request start / fail
- analysis request start / completed
- DB write quan trọng

## 15.2 Không log dữ liệu nhạy cảm
Không log:
- password
- token
- secret key
- raw private user data

---

# 16. BACKEND CONFIG RULES

## 16.1 Không hardcode config
Tất cả config phải đi qua:
- `.env`
- `config.py`

Ví dụ:
- DB URL
- OpenAI API Key
- JWT secret
- token expiry
- crawl schedule

---

# 17. BACKEND BUSINESS LOGIC RULES CHO DỰ ÁN NÀY

## 17.1 Phải tách riêng logic tính toán chỉ số
Các chỉ số như:
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

phải nằm ở các file/module riêng.

### Gợi ý
```text
modules/indicators/
├── technical.py
├── fundamental.py
├── scoring.py
└── validators.py
```

---

## 17.2 OpenAI logic phải tách riêng
Không được nhét prompt vào route hoặc service lẫn lộn.

### Gợi ý
```text
modules/ai_analysis/
├── prompt_builder.py
├── client.py
├── parser.py
├── schemas.py
└── service.py
```

---

## 17.3 Crawler logic phải tách riêng
Không được viết crawler như utility linh tinh.

### Gợi ý
```text
modules/crawler/
├── clients/
├── parsers/
├── normalizers/
├── jobs/
├── service.py
└── repository.py
```

---

# 18. BACKEND CODE STYLE RULES

## 18.1 Python style
- tuân thủ PEP8
- import gọn, rõ
- không wildcard import
- ưu tiên type hints

### Đúng
```python
def calculate_rsi(prices: list[float], period: int = 14) -> float:
    ...
```

---

## 18.2 Docstring rule
Chỉ viết docstring cho:
- function phức tạp
- service quan trọng
- helper dễ gây hiểu nhầm

Không cần docstring cho code quá hiển nhiên.

---

# 19. BACKEND TESTING RULES

## 19.1 Phải test cho phần sau
Bắt buộc test:
- business logic
- scoring logic
- indicator calculations
- mapper / parser quan trọng
- auth logic

## 19.2 Không cần over-test
Không cần unit test cho:
- getter đơn giản
- code quá trivial

## 19.3 Ưu tiên test cho:
- `calculate_rsi`
- `calculate_macd`
- `calculate_fundamental_score`
- `build_stock_analysis_payload`
- `parse_openai_analysis_result`

---

# 20. FRONTEND RULES — TYPESCRIPT + NEXT.JS

---

# 21. FRONTEND KIẾN TRÚC BẮT BUỘC

Frontend không được viết kiểu:
- page fetch hết
- render hết
- logic hết
- state hết

=> sẽ rất nhanh rối.

Frontend phải tách rõ:

- page
- feature components
- ui components
- hooks
- services
- types
- state

---

# 22. FRONTEND FOLDER RULES

## 22.1 Cấu trúc khuyến nghị

```text
frontend/
├── app/
│   ├── login/
│   ├── register/
│   ├── dashboard/
│   ├── stocks/
│   │   └── [ticker]/
│   ├── history/
│   └── admin/
├── components/
│   ├── ui/
│   ├── common/
│   ├── stock/
│   ├── analysis/
│   └── admin/
├── hooks/
├── services/
├── lib/
├── types/
├── constants/
├── utils/
└── middleware.ts
```

---

# 23. FRONTEND PAGE RULES

## 23.1 Page chỉ nên orchestration
Page nên:
- lấy params
- gọi hooks / server actions / services
- render layout
- truyền props xuống component

## 23.2 Page không nên:
- chứa logic xử lý dữ liệu quá nhiều
- chứa JSX dài hàng trăm dòng
- chứa business logic phân tích cổ phiếu

---

# 24. FRONTEND COMPONENT RULES

## 24.1 Component phải nhỏ, rõ vai trò
Ví dụ tốt:
- `StockHeader`
- `PriceSummaryCard`
- `TechnicalIndicatorCard`
- `AIRecommendationPanel`
- `AnalysisHistoryTable`

## 24.2 Không làm component “quái vật”
### Sai
```tsx
<StockAnalysisEverythingComponent />
```

---

# 25. FRONTEND PRESENTATIONAL VS CONTAINER RULES

## 25.1 Presentational component
Chỉ nhận props và render UI.

Ví dụ:
- card
- chart wrapper
- table row
- badge
- section title

## 25.2 Container / feature component
Chứa:
- data fetching
- derived state
- orchestration

Ví dụ:
- `StockAnalysisSection`
- `AdminUsersTableContainer`

---

# 26. FRONTEND TYPESCRIPT RULES

## 26.1 Không dùng `any` bừa bãi
### Sai
```ts
const data: any = await fetchSomething();
```

### Đúng
```ts
const data: StockAnalysisResponse = await fetchSomething();
```

---

## 26.2 Mọi API response phải có type riêng
Ví dụ:
```ts
export interface StockDetailResponse {
  ticker: string;
  companyName: string;
  exchange: string;
  sector: string;
}
```

---

# 27. FRONTEND TYPE ORGANIZATION RULES

## 27.1 Tách type theo domain
Ví dụ:
```text
types/
├── auth.ts
├── stock.ts
├── analysis.ts
├── admin.ts
└── common.ts
```

---

# 28. FRONTEND DATA FETCHING RULES

## 28.1 Không fetch API bừa bãi trong nhiều component
Phải có chiến lược rõ ràng.

## 28.2 Rule khuyến nghị
- fetch chính ở page hoặc container
- component con chỉ nhận data qua props
- tránh mỗi component tự call API nếu không cần

---

# 29. FRONTEND SERVICE RULES

## 29.1 Tất cả API call phải đi qua `services/`
Ví dụ:
```text
services/
├── auth.service.ts
├── stock.service.ts
├── analysis.service.ts
└── admin.service.ts
```

### Không được:
- viết `fetch(...)` rải rác khắp component

---

## 29.2 Service phải có hàm rõ nghĩa
Ví dụ:
- `loginUser`
- `registerUser`
- `getStockDetail`
- `getStockPriceHistory`
- `requestStockAnalysis`
- `getAnalysisHistory`

---

# 30. FRONTEND HOOK RULES

## 30.1 Hook chỉ dùng khi thực sự có reusable logic
Không phải cái gì cũng nhét vào hook.

## 30.2 Nên tạo hook cho:
- auth state
- debounce search
- pagination
- stock detail state
- analysis polling (nếu async)

Ví dụ:
- `useAuth`
- `useStockDetail`
- `useAnalysisHistory`

---

# 31. FRONTEND STATE RULES

## 31.1 Chỉ lưu state thật sự cần
Không được nhét mọi thứ vào global state.

## 31.2 Chia state hợp lý
- local UI state → component
- feature state → hook / context
- auth/session → global hoặc provider phù hợp

---

# 32. FRONTEND UI RULES

## 32.1 UI phải phục vụ dữ liệu
Đây là hệ thống tài chính / phân tích.

=> UI phải:
- rõ
- sạch
- dễ scan
- ưu tiên thông tin hơn hiệu ứng

## 32.2 Không được:
- animation quá nhiều
- màu sắc gây rối
- nhồi quá nhiều card vô nghĩa

---

# 33. FRONTEND RENDER RULES CHO DỰ ÁN NÀY

## 33.1 Một trang mã cổ phiếu nên tách thành các section rõ ràng

### Ví dụ
- Header thông tin mã
- Price chart
- Fundamental metrics
- Technical indicators
- Internal scores
- AI analysis
- Analysis history

Không được nhét tất cả vào 1 component lớn.

---

# 34. FRONTEND CHART RULES

## 34.1 Chart phải tách riêng
Ví dụ:
- `PriceHistoryChart`
- `VolumeChart`
- `RSIChart`
- `MACDChart`

## 34.2 Không xử lý business logic trong chart component
Chart component chỉ:
- nhận data đã chuẩn
- render chart

---

# 35. FRONTEND FORM RULES

## 35.1 Form phải có:
- validation
- loading state
- error state
- disabled state khi submit

## 35.2 Không submit “mù”
Mọi form auth/admin đều phải:
- validate trước
- show error rõ ràng

---

# 36. FRONTEND ERROR HANDLING RULES

## 36.1 Không swallow lỗi
Phải hiển thị:
- lỗi user hiểu được
- fallback state phù hợp

Ví dụ:
- “Không thể tải dữ liệu cổ phiếu”
- “Không thể tạo phân tích lúc này”

---

# 37. FRONTEND LOADING RULES

## 37.1 Mọi màn hình fetch dữ liệu phải có loading state
Ví dụ:
- stock detail page
- history page
- admin table
- AI analysis page

## 37.2 Không để màn hình trắng
Phải có:
- skeleton
- spinner
- placeholder phù hợp

---

# 38. FRONTEND REUSABILITY RULES

## 38.1 Chỉ tái sử dụng khi thực sự hợp lý
Không ép trừu tượng quá sớm.

### Sai
Tạo generic component siêu phức tạp chỉ để “có vẻ reusable”.

### Đúng
Trước tiên viết rõ ràng, sau đó khi lặp 2–3 lần thì refactor.

---

# 39. FRONTEND STYLING RULES

## 39.1 Phải thống nhất style system
Nếu dùng Tailwind:
- dùng nhất quán
- tránh style inline bừa bãi

## 39.2 Không hardcode style lặp đi lặp lại
Tạo reusable UI primitives cho:
- button
- card
- badge
- section
- table
- modal

---

# 40. FRONTEND SECURITY RULES

## 40.1 Không lưu token bừa bãi
Không được:
- log token ra console
- hardcode secret
- expose internal config

## 40.2 Không trust dữ liệu FE
Frontend chỉ hỗ trợ UX.
Validation thực sự vẫn phải ở backend.

---

# 41. API CONTRACT RULES (BE ↔ FE)

Đây là phần rất quan trọng.

---

# 42. RESPONSE FORMAT PHẢI ỔN ĐỊNH

## 42.1 Thành công
```json
{
  "data": {},
  "message": "Success"
}
```

## 42.2 Lỗi
```json
{
  "message": "Stock not found",
  "error_code": "STOCK_NOT_FOUND"
}
```

> Không được API mỗi chỗ trả 1 kiểu khác nhau.

---

# 43. FIELD NAMING BE ↔ FE

## Rule
API JSON nên thống nhất dùng:
- `snake_case` hoặc `camelCase`

### Khuyến nghị mạnh:
Dùng **`snake_case` ở backend nội bộ**, nhưng **response API trả về `camelCase` cho frontend** nếu team FE muốn dễ dùng.

### Nhưng:
Chỉ được chọn **1 quy ước chính thức** và giữ thống nhất toàn hệ thống.

> Khuyến nghị thực tế cho dự án này:
> **API response dùng `camelCase`**
> để FE Next.js dùng dễ hơn.

---

# 44. KHÔNG ĐƯỢC PHÁ API CONTRACT TÙY TIỆN

Nếu thay đổi API:
- phải update type FE
- phải update docs
- phải review impact

Không được tự ý đổi:
- field name
- enum values
- response shape

---

# 45. RULES CHO OPENAI INTEGRATION

---

# 46. BACKEND RULES CHO OPENAI

## 46.1 Không gửi raw dữ liệu rác lên AI
Trước khi gửi AI phải:
- validate
- normalize
- summarize có cấu trúc

## 46.2 Prompt phải version hóa
Phải lưu prompt trong:
- file config
- hoặc DB table `ai_prompt_configs`

Không hardcode prompt quan trọng rải rác.

---

# 47. FRONTEND RULES CHO OPENAI OUTPUT

## 47.1 Không render raw text vô tổ chức
Phải render AI output theo section:

- Summary
- Fundamental Analysis
- Technical Analysis
- Risks
- Conclusion
- Recommendation

## 47.2 Nếu AI response lỗi format
Frontend phải có fallback UI:
- “Không thể hiển thị kết quả phân tích”
- không được crash màn hình

---

# 48. PERFORMANCE RULES

## Backend
- tránh query N+1
- index các field quan trọng
- cache nếu cần
- không gọi OpenAI dư thừa

## Frontend
- tránh rerender không cần thiết
- lazy load phần nặng nếu cần
- chart data nên memo nếu lớn

---

# 49. GIT & TEAMWORK RULES

## 49.1 Không commit:
- `.env`
- secret
- key
- build artifacts
- cache file

## 49.2 Commit message nên rõ
Ví dụ:
- `feat: add stock analysis history endpoint`
- `fix: handle missing financial data in scoring`
- `refactor: extract technical indicator calculation service`

---

# 50. FINAL ENGINEERING RULES

## Rule 1
**Không được viết code “chạy được là xong”.**

## Rule 2
**Mọi logic quan trọng phải có chỗ ở rõ ràng.**

## Rule 3
**Tên hàm / tên biến phải phản ánh đúng hành vi.**

## Rule 4
**BE không được ôm UI concerns.**

## Rule 5
**FE không được ôm business logic tài chính phức tạp.**

## Rule 6
**OpenAI chỉ là lớp giải thích, không phải lõi tính toán.**

## Rule 7
**Nếu một đoạn code khiến người khác phải đoán, coi như code đó chưa đạt.**

---

# 51. KẾT LUẬN

Với dự án này, chất lượng sản phẩm sẽ phụ thuộc rất mạnh vào:

- chất lượng dữ liệu crawl
- chất lượng logic tính chỉ số
- chất lượng API contract
- chất lượng tổ chức code

Nếu tuân thủ đúng rule này, hệ thống sẽ:

- dễ mở rộng từ 1 mã → nhiều mã
- dễ maintain
- dễ onboarding dev mới
- dễ review
- dễ deploy production

> Mục tiêu không phải chỉ là “code chạy được”.
>
> Mục tiêu là xây một **sản phẩm doanh nghiệp có thể sống lâu**.
