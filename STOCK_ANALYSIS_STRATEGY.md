# STOCK ANALYSIS PLATFORM — SYSTEM DESIGN & STRATEGY
**Scope:** thị trường chứng khoán Việt Nam, bắt đầu 1 mã.

**Giới hạn tài liệu:** toàn bộ file này giữ **≤ 20.000 ký tự**; payload mẫu / ingest thủ công **≤ 20.000 ký tự** mỗi lần (chia lô nếu dài).

---

## 1. Mục tiêu
- Nền tảng phân tích cổ phiếu: dữ liệu → chỉ số → điểm nội bộ → OpenAI diễn giải.
- Crawl giá từng mã (VietStock `GetStockDeal_ListPriceByTimeFrame`), lưu DB, chỉ báo kỹ thuật / cơ bản.

---

## 2. Dữ liệu đầu vào (JSON giá)

**2.1 ListPrice** — `data.ListPrice_Results` (POST: `stockCode`, `timeFrame=C`, `toDate`, `page=1`, `pageSize≤20`, `languageID`, token).

```json
{"data":{"ListPrice_Results":[{"StockCode":"HPG","TradingDate":"/Date(1775667600000)/","OpenPrice":27900,"HighestPrice":28600,"LowestPrice":27650,"ClosePrice":28250,"Change":250,"PerChange":0.89,"TotalVol":52046100}],"ListPrice_Summary_Results":[{"TotalRow":1}]}}
```

**2.2 Chỉ số / chart** — `data[]` với `OpenIndex`…`CloseIndex`.

```json
{"data":[{"TradingDate":"/Date(1232643600000)/","OpenIndex":300.48,"HighestIndex":300.48,"LowestIndex":300.48,"CloseIndex":300.48,"Change":1.99,"PerChange":0.67,"TotalVol":1909141}]}
```

`TradingDate`: `/Date(ms)/` hoặc ISO. Parser map: ListPrice → `OpenPrice`…; chỉ số → `OpenIndex`… → OHLCV nội bộ.

---

## 3. Năm lớp dữ liệu (tóm tắt)
| Lớp | Nội dung chính |
|-----|----------------|
| Giá | OHLCV, % change, (value, cap nếu có) |
| Cơ bản | BCTC, EPS, ROE, P/E, tăng trưởng… |
| Hồ sơ DN | Ticker, ngành, mô tả, sàn |
| Tin / sự kiện | KQKD, cổ tức, M&A… |
| Snapshot phân tích | Điểm số, AI output, lưu lịch sử |

Chỉ có giá **chưa đủ** cho phân tích đầu tư đầy đủ.

---

## 4. Pipeline
1. Thu thập (crawl + chuẩn hóa) → 2. Chỉ báo & metric → 3. Fundamental / Technical / Risk score → 4. **Engine JSON đầy đủ** (không `null` cho khóa đã cam kết — xem dưới) → 5. **Gói cho OpenAI** (`engine` + `fundamental_context` trong payload) → 6. Lưu `analysis_results`.

**Góc nhìn:** (A) Cơ bản — tăng trưởng, biên, nợ, định giá. (B) Kỹ thuật — xu hướng, RSI/MACD, volume, hỗ trợ/kháng cự. (C) Rủi ro — biến động, nợ, sự kiện.

**Điểm 0–100 (gợi ý):** Fundamental: growth, ROE, margin, nợ, valuation. Technical: trend, RSI, MACD, volume. Risk: càng cao càng rủi ro (hoặc đảo thành safety).

**`normalized_features_for_ai` (backend):** cùng phiên cuối với `indicators`, nhiều mục % / 0–1 / nhãn; `null` nội bộ được thay bằng `"unavailable"` trước khi serialize. Chi tiết: `stock_analysis_strategy_engine.md` **§32.5–32.6**.

**Độ đầy đủ engine (Data completeness):** `indicators`, `levels`, vùng giá trong `risk` dùng sentinel số rất âm (≈ −10⁷) khi không có snapshot; `latest_price.change`/`change_pct` thiếu → `0.0`; `fundamental_metrics` luôn object (`status`: `available` | `unavailable`); `latest_financial_report` tương tự; thêm `confidence` (0–100), `computed_bias` (bullish/bearish/neutral), `signal_summary` (4 chuỗi). Mã: `engine_completeness.py`, `pipeline.py`, service phân tích ghi đè cơ bản/BCTC. Chi tiết: **§32.6** và **§33.1** trong `stock_analysis_strategy_engine.md`.

**OpenAI:** chỉ diễn giải số đã tính (gồm `confidence`, `computed_bias`, `signal_summary`); output JSON gợi ý: `summary`, `fundamental_analysis`, `technical_analysis`, `risks[]`, `conclusion`, `recommendation`, `fundamental_data_gaps`, `fundamental_wishlist`. Prompt: không bịa số; fundamental khi `status=unavailable` dùng câu cố định theo template (không “thiếu dữ liệu” chung chung).

---

## 5. Stack & kiến trúc
Next.js → FastAPI → MySQL; OpenAI; Docker. Crawler/scheduler nền.

**Module:** Auth, Stock, **Crawler** (27.3.1), Indicator, AI Analysis, History, Admin.

### 5.1 Crawl giá VietStock (triển khai)
- **Chỉ cổ phiếu:** `POST …/data/GetStockDeal_ListPriceByTimeFrame` — body chỉ gồm `stockCode`, `timeFrame`, `toDate`, `page`, `pageSize`, `languageID`, `__RequestVerificationToken` (backend lọc field khác).
- **`crawl_metadata_json`:** tùy chọn — thiếu hoặc null thì API crawl vẫn chạy với URL/strategy mặc định trong code. Nếu có: `url`, `form`, `session`, `crawl_strategy`, `headers` / `referer_template`.
- **`stockCode`** khi gọi API luôn = **ticker** trong DB.
- **Lùi ngày:** vòng 1 `toDate` = `initial_to_date`; mỗi vòng `page=1`; `toDate` tiếp = `min(TradingDate)` trong batch **− 1 ngày**; tới khi hết dữ liệu hoặc `max_rounds` (~500). Gộp trùng ngày.
- **`initial_to_date`:** `today` = ngày **Asia/Ho_Chi_Minh**; `oldest_in_db_minus_1` = `min(trading_date)` trong DB − 1 (backfill / lịch).
- **`page_size`:** API tối đa **20**; backend clamp **>20→20**, **<1→1**.
- **Ingest ListPrice:** `skip_locked_historical`: đã có bản ghi và ngày **≠ hôm nay VN** → skip; hôm nay → upsert; ngày mới → insert; trùng nội dung → skip. Log: `inserted`, `updated`, `skipped`.
- **Lịch:** `crawl_schedules` gọi cùng `trigger_vietstock_crawl`; cookie/token trên lịch.
- **API:** `POST .../admin/crawl/{ticker}` (ingest JSON); `POST .../admin/crawl/vietstock/{ticker}` (VietStock theo metadata).

---

## 6. DB tối thiểu (tên bảng & cột chính)
- **users** — id, email, password_hash, role, status, timestamps.
- **stocks** — ticker, company_name, exchange, sector, description, `crawl_metadata_json`, …
- **stock_price_histories** — stock_id, trading_date, open/high/low/close, price_change, percent_change, total_volume, raw_payload_json.
- **stock_financial_reports** / **stock_key_metrics** / **stock_technical_indicators** — theo nhu cầu phase.
- **analysis_requests**, **analysis_results** — snapshot + scores + AI fields + raw_ai_response_json.
- **crawl_logs** — stock_id, crawl_type, status, message, started/finished_at.
- **crawl_schedules** — stock_id, interval, cookie/token, next_run, last_run_*
- **ai_prompt_configs** — prompt templates.

Mapping giá: `TradingDate`→`trading_date`; ListPrice `OpenPrice`… hoặc chỉ số `OpenIndex`…→ OHLC tương ứng; `TotalVol`→`total_volume`.

---

## 7. API (gợi ý path)
Auth: register, login, me. Stocks: list, `{ticker}`, prices, metrics, technicals. Analysis: POST analyze, history. Admin: users, stocks, crawl, crawl/logs, analysis.

---

## 8. Triển khai & MVP
**Thứ tự:** crawl giá → DB → chỉ báo → (sau) BCTC/metric → scoring → OpenAI → UI/admin.

**MVP:** 1 mã; giá + SMA/EMA/RSI/MACD/Bollinger + vài metric; AI + lịch sử; admin crawl/metadata.

---

## 9. Nguyên tắc
> **Data trước → tính toán sau → AI cuối.** AI là lớp giải thích, không thay thế quy tắc phân tích và dữ liệu.
