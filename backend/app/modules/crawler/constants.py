"""Hằng số cho crawler VietStock — giới hạn API, vòng lặp, v.v. (không ghi đè qua env)."""

from __future__ import annotations

# API VietStock chỉ chấp nhận pageSize tối đa ~20 cho ListPrice.
VIETSTOCK_API_MAX_PAGE_SIZE: int = 20

# Số vòng lùi toDate tối đa khi metadata không chỉ định crawl_strategy.max_rounds.
DEFAULT_VIETSTOCK_MAX_ROUNDS: int = 500

# Đường dẫn trang thống kê giao dịch theo mã (dùng làm Referer mặc định).
VIETSTOCK_STOCK_TRADING_STATS_PATH: str = "thong-ke-giao-dich.htm"
