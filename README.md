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
