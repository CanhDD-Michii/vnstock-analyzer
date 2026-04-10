# vnstock-analyzer

Nền tảng phân tích cổ phiếu Việt Nam: **chuỗi giá → chỉ báo kỹ thuật & điểm số nội bộ → dữ liệu cơ bản gộp → AI diễn giải có cấu trúc** — minh bạch nguồn số, không thay thế quyết định đầu tư của nhà đầu tư.

---

## Vì sao sản phẩm này khác biệt?

Trên thị trường, nhiều công cụ chỉ **hiển thị** biểu đồ hoặc đưa **nhận định chung chung**. **vnstock-analyzer** đi theo hướng **pipeline rõ ràng**: mọi nhận định AI đều bám **JSON do engine tính sẵn** (điểm 0–100, trạng thái thị trường, vùng giá, rủi ro, chỉ số cơ bản đã gộp). AI **không tự bịa số** — chỉ **diễn giải** và **gợi ý khuyến nghị** theo schema cố định, phù hợp môi trường tuân thủ và kiểm chứng.

---

## Phân tích kỹ thuật — engine có “chiều sâu”

Hệ thống xây **feature engineering** và **scoring** trên OHLCV (cần đủ lịch sử phiên để các MA dài hạn ổn định):

| Lớp | Nội dung chính |
|-----|-----------------|
| **Xu hướng** | SMA/EMA, độ dốc MA, căn chỉnh MA (bull/bear stack), khoảng cách giá so với MA |
| **Động lượng** | RSI (Wilder), MACD + histogram + gợi ý cắt tín hiệu, Stochastic, ROC |
| **Thanh khoản** | Tỷ số volume so SMA 20, xu hướng volume; **điểm volume** luôn trong vùng hợp lý (không “tụt về 0” làm mất tín hiệu) |
| **Biến động** | ATR, Bollinger (width, vị trí giá trong dải), độ lệch chuỗi lợi nhuận ngày |
| **Cấu trúc & rủi ro** | Đỉnh/đáy rolling, proxy drawdown, mức hỗ trợ/kháng cự gần, lớp rủi ro |

**Điểm 0–100** theo từng trục: `trend`, `momentum`, `volume`, `volatility`, `risk`, `breakout` — cộng hợp thành **technical score** và **trạng thái thị trường** (state machine). Thêm **`confidence`** (trung bình có trọng số các score kỹ thuật, volume không chi phối quá mức) và **`computed_bias`** (bullish / bearish / weak_bullish / weak_bearish / neutral) để prompt và UI thống nhất ngôn ngữ.

Payload cho AI còn có **`normalized_features_for_ai`**: các đại lượng đã chuẩn hóa (% lệch MA, vùng RSI, trạng thái MACD so signal, v.v.) giúp mô hình đọc nhanh mà không đè lên vai trò của `scores` và rule engine.

---

## Phân tích cơ bản — 12 chỉ số, một luồng gộp

Không dừng ở “có hay không có BCTC”. Khi chạy **phân tích đầy đủ**, hệ thống **gộp** snapshot **12 khóa** chuẩn:

`pe`, `pb`, `roe`, `roa`, `gross_margin`, `net_margin`, `debt_to_equity`, `current_ratio`, `quick_ratio`, `revenue_growth_yoy`, `profit_growth_yoy`, `eps_growth_yoy`

- **Ưu tiên** số từ bảng **key metrics** (crawl/nhập).  
- **Bổ sung** phần suy được từ **hai kỳ BCTC gần nhất** (biên, ROE/ROA, đòn bẩy, tăng trưởng YoY).  
- **P/E, P/B suy ra** từ **giá đóng cửa** và EPS/BVPS BCTC mới nhất khi DB chưa có.  

Từ đó có **`fundamental_score`** (0–100) và **`fundamental_context`** (đủ/khóa thiếu, nhãn tiếng Việt) đưa vào prompt — AI biết chính xác **đang có những số nào** và **còn trống chỗ nào**.

---

## Ứng dụng AI — đúng vai trò “interpreter”

- **Input:** `engine` + `fundamental_context` (và hướng dẫn không bịa dữ liệu).  
- **Output JSON cố định:** tóm tắt 4 trục, phân tích cơ bản/kỹ thuật, rủi ro, kết luận, **mã khuyến nghị**, danh sách **khoảng trống dữ liệu** và **wishlist** bổ sung.  
- **Prompt** ép lập luận gắn số, hạn chế câu chung chung, bắt xác định bias và hành động ngắn hạn/dài hạn rõ ràng.  
- **Parser** chuẩn hóa cả trường hợp model trả **object** thay vì chuỗi — tránh lỗi hiển thị ở UI và DB.

Kết quả đạt được: **một luồng sản phẩm khép kín** — từ dữ liệu thô → chỉ số → điểm → **bản phân tích có cấu trúc, truy vết được** (lưu `analysis_results`, lịch sử theo user).

---

## Giao diện & vận hành

- **Next.js**: chi tiết mã, biểu đồ nến OHLC và đường giá đóng, **xem chart toàn màn hình** (icon), chạy phân tích và xem **khối AI** (khuyến nghị, tóm tắt, cơ bản, kỹ thuật, rủi ro, kết luận).  
- **FastAPI + MySQL**: API chứng thực, lưu giá, metrics, BCTC, lịch sử phân tích.  
- **Docker Compose**: backend, frontend, MySQL; biến môi trường cho OpenAI (tắt API key vẫn có **fallback** rule-based để demo không gãy).

---

## Ai nên dùng?

- Đội sản phẩm / cá nhân muốn **demo pipeline** “data → signal → narrative” cho thị trường Việt Nam.  
- Người cần **khung phân tích nhất quán** (kỹ thuật + cơ bản + rủi ro) trước khi tự ra quyết định.  
- Team kỹ thuật muốn **mở rộng** crawler, thêm chỉ báo, hoặc tinh chỉnh prompt/score theo `stock_analysis_strategy_engine.md` và `STOCK_ANALYSIS_STRATEGY.md`.

---

## Lưu ý pháp lý & đầu tư

Công cụ chỉ hỗ trợ **phân tích và minh họa quy trình**; **không phải** lời khuyên đầu tư có thù lao. Mọi quyết định mua/bán thuộc về người dùng; dữ liệu và AI có thể **sai lệch hoặc lỗi thời** — luôn đối chiếu nguồn chính thống và quản trị rủi ro vốn.

---

## Bắt đầu nhanh

```bash
# Sao chép biến môi trường và chỉnh DATABASE_URL / OPENAI_API_KEY nếu cần
cp .env.example .env

docker compose up --build
```

- Backend: cổng mặc định **8000** (xem `docker-compose.yml`).  
- Frontend: cổng mặc định **3000**.  
- Tài liệu chiến lược & engine: **`STOCK_ANALYSIS_STRATEGY.md`**, **`stock_analysis_strategy_engine.md`**.

---

**vnstock-analyzer** — *từ dữ liệu giá và báo cáo đến nhận định có cấu trúc, với AI làm lớp diễn giải minh bạch trên nền chỉ số đã tính.*

```
https://finance.vietstock.vn/HPG/thong-ke-giao-dich.htm
curl --location 'https://finance.vietstock.vn/data/GetStockDeal_ListPriceByTimeFrame' \
--header 'Accept: application/json, text/javascript, */*; q=0.01' \
--header 'Accept-Language: en-US,en;q=0.9,vi;q=0.8' \
--header 'Cache-Control: no-cache' \
--header 'Connection: keep-alive' \
--header 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
--header 'Origin: https://finance.vietstock.vn' \
--header 'Pragma: no-cache' \
--header 'Referer: https://finance.vietstock.vn/HPG/thong-ke-giao-dich.htm' \
--header 'Sec-Fetch-Dest: empty' \
--header 'Sec-Fetch-Mode: cors' \
--header 'Sec-Fetch-Site: same-origin' \
--header 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36' \
--header 'X-Requested-With: XMLHttpRequest' \
--header 'sec-ch-ua: "Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"' \
--header 'sec-ch-ua-mobile: ?0' \
--header 'sec-ch-ua-platform: "Linux"' \
--header 'Cookie: __qca=I0-215144766-1775705967305; language=vi-VN; ASP.NET_SessionId=jhq4yedd0klrmh3bk33qyi1s; __RequestVerificationToken=yaALrJUfINpfGgTTj7JdKXX42EvZCKCsPFMlVknMA61nBBz19NJ5p0_MPfsK-HbA1BUxIQxqbULG7HF5BxpAfYV6detD8Kxf_YG0IT1cqX41; Theme=Light; AnonymousNotification=; _gid=GA1.2.967215515.1775705965; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%224d4a9b60-4130-4fea-9203-0470789a07b1%5C%22%2C%5B1775705966%2C89000000%5D%5D%22%5D%5D%5D; isShowLogin=true; CookieLogin=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiY2FuaGRkOTdkZXZlbG9wZXJAZ21haWwuY29tIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvaGFzaCI6InNrLVllSU5vUzhoY3hhLXpIQThmYjJvcFEiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6ImNhbmhkZDk3ZGV2ZWxvcGVyQGdtYWlsLmNvbSIsImV4cCI6MTc3ODI5ODI1OSwiaXNzIjoiLnZpZXRzdG9jay52biIsImF1ZCI6Ii52aWV0c3RvY2sudm4ifQ.oTddLUELRQ1ag8ftWaBvP1tMvJhCuv60HANt07-NobQ; vst_usr_lg_token=0UwGDyBpB0iaL9daQppQ6A==; __qca=I0-889593344-1775728018576; finance_viewedstock=MWG,LPB,FPT,HPG,; finance_viewedstock_v2=MWG,LPB,FPT,HPG,; _ga=GA1.2.2076316315.1775705964; cto_bidid=Dm1RsF9LY2FzSWlZdlo1c2I2MndjVWYzNEx2ZVJyRjhCcFQ3RVhTdVh2a29VdjA2ZmlRcFJtRyUyRnVSdmxYWm1kOGlmYkV3ZUdBbGNBZFQxdVc1MnhHQiUyQk9GQU13aFBXaDQ4JTJGRFh1elZyU09BdndmSSUzRA; __gads=ID=0e2833798d4769ca:T=1775705966:RT=1775730222:S=ALNI_MY9tvIUZQmLytZT-ChajS8q03aVVA; __gpi=UID=000012434fd5223f:T=1775705966:RT=1775730222:S=ALNI_MZkX0ZkEoml7e3JkHxXje-XEpaWsA; __eoi=ID=18b7a07914fe5e82:T=1775705966:RT=1775730222:S=AA-AfjZfscz882MRxmJKJknmuPxO; FCNEC=%5B%5B%22AKsRol8j12wFAx6BvRCT6syq_QCVBaSN_kmq_jXpjXOujFScQE4nmgtT998FwbUqTLHpNDztQLtpxolFmStz7hXgGn63I4aZdB0IHyxFUIwrzpdSxw1gPcu-GTTX5G6qGEJwBUV31GspSjs-bUx59jj6h_Q6e0u1CA%3D%3D%22%5D%5D; cto_bundle=i84hr18lMkJKNTdLJTJCOHpGb0ElMkJpQ1RsWHNCTjljZ0xDSThCJTJGdSUyQmxQYUhVWUlNRE9vNVRFUzdBTGdDNW5lcUpzNzUlMkZhcmpqeWZ6VUVMdG5FaUo1MlViRTd1cmdnWXp3SGpJS0lsWGZhelZqckVBRSUyQm41ckMwbzJvNkN0QVZzcU04eXdFWVcyVnlSeEV3SEdpMTBBYjA4Wk9adldkUSUzRCUzRA; _ga_EXMM0DKVEX=GS2.1.s1775728017$o2$g1$t1775730514$j60$l0$h0; language=vi-VN' \
--data 'stockCode=VHM&timeFrame=C&toDate=2026-04-09&page=1&pageSize=2&languageID=1&__RequestVerificationToken=PyePwXp-vYEP8981KWqcxD-8RAgTNVpIjoOR4fS9_038KFv3tz3QajmhSp8UO_RW91daffTdlgHJjBv9fDkJBdpOzbVFrtr4d7myYoQxq2zUFsvl5gTD7iA3qH-Kvh-EuHEdlmjDC5m2SlhY4mF3dQ2'
```
