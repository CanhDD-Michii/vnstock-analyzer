from __future__ import annotations

from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, StockNotFoundError
from app.db.models import AnalysisResult, CrawlLog, Stock, User, UserRole, UserStatus
from app.modules.analysis_history.repository import AnalysisHistoryRepository
from app.modules.admin.schemas import StockCreateBody, StockPatchBody, UserPatchBody, VietstockCrawlBody
from app.modules.crawler.service import CrawlerService
from app.modules.crawler.vietstock_client import fetch_vietstock_price_series
from app.modules.stocks.repository import StockRepository
from app.modules.users.repository import UserRepository


class AdminService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._stocks = StockRepository(db)
        self._crawler = CrawlerService(db)
        self._analysis = AnalysisHistoryRepository(db)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self._users.list_users(skip=skip, limit=limit)

    def _count_active_admins_excluding(self, exclude_user_id: int) -> int:
        q = select(func.count(User.id)).where(
            User.role == UserRole.admin.value,
            User.status == UserStatus.active.value,
            User.id != exclude_user_id,
        )
        return int(self._db.scalar(q) or 0)

    def patch_user(self, user_id: int, body: UserPatchBody, acting_admin: User) -> User:
        u = self._users.get_by_id(user_id)
        if not u:
            raise AppError("Không tìm thấy người dùng", "USER_NOT_FOUND", status_code=404)

        set_fn = "full_name" in body.model_fields_set and body.full_name is not None
        set_role = "role" in body.model_fields_set and body.role is not None
        set_status = "status" in body.model_fields_set and body.status is not None

        if not (set_fn or set_role or set_status):
            raise AppError("Không có trường nào để cập nhật", "EMPTY_PATCH", status_code=400)

        new_full = body.full_name.strip() if set_fn else u.full_name
        new_role = body.role if set_role else u.role
        new_status = body.status if set_status else u.status

        if set_fn and not new_full:
            raise AppError("Họ tên không được để trống", "INVALID_FULL_NAME", status_code=400)

        was_active_admin = (
            u.role == UserRole.admin.value and u.status == UserStatus.active.value
        )
        will_be_active_admin = (
            new_role == UserRole.admin.value and new_status == UserStatus.active.value
        )

        if user_id == acting_admin.id:
            if set_status and new_status == UserStatus.inactive.value:
                raise AppError(
                    "Không thể tự vô hiệu tài khoản của chính mình",
                    "SELF_DEACTIVATE",
                    status_code=400,
                )

        if was_active_admin and not will_be_active_admin:
            if self._count_active_admins_excluding(u.id) < 1:
                raise AppError(
                    "Phải có ít nhất một tài khoản admin đang hoạt động",
                    "LAST_ADMIN",
                    status_code=409,
                )

        updated = self._users.patch_user(
            user_id,
            full_name=new_full if set_fn else None,
            set_full_name=set_fn,
            role=new_role if set_role else None,
            set_role=set_role,
            status=new_status if set_status else None,
            set_status=set_status,
        )
        if not updated:
            raise AppError("Không tìm thấy người dùng", "USER_NOT_FOUND", status_code=404)
        return updated

    def list_stocks(self, skip: int = 0, limit: int = 200) -> list[Stock]:
        q = select(Stock).order_by(Stock.ticker).offset(skip).limit(limit)
        return list(self._db.scalars(q).all())

    def trigger_price_crawl(self, ticker: str, items: list[dict[str, Any]]) -> tuple[int, int]:
        stock = self._stocks.get_by_ticker(ticker)
        if not stock:
            raise StockNotFoundError()
        return self._crawler.ingest_price_json(stock, items)

    def create_stock(self, body: StockCreateBody) -> Stock:
        t = body.ticker.strip().upper()
        meta = body.crawl_metadata if isinstance(body.crawl_metadata, dict) else None
        try:
            return self._stocks.create_stock(
                ticker=t,
                company_name=body.company_name.strip(),
                exchange=(body.exchange or "").strip(),
                sector=(body.sector or "").strip(),
                description=body.description.strip() if body.description else None,
                crawl_metadata_json=meta,
            )
        except IntegrityError:
            self._db.rollback()
            raise AppError("Ticker đã tồn tại", "STOCK_DUPLICATE", status_code=409) from None

    def patch_stock(self, ticker: str, body: StockPatchBody) -> Stock:
        t = ticker.strip().upper()
        set_meta = "crawl_metadata" in body.model_fields_set
        if set_meta and body.crawl_metadata is not None and not isinstance(body.crawl_metadata, dict):
            raise AppError("crawlMetadata phải là object JSON", "INVALID_METADATA", status_code=400)
        set_co = "company_name" in body.model_fields_set and body.company_name is not None
        stock = self._stocks.patch_stock_admin(
            t,
            company_name=body.company_name,
            set_company_name=set_co,
            crawl_metadata_json=body.crawl_metadata if set_meta else None,
            set_crawl_metadata=set_meta,
        )
        if not stock:
            raise StockNotFoundError()
        return stock

    def trigger_vietstock_crawl(self, ticker: str, body: VietstockCrawlBody) -> tuple[int, int]:
        stock = self._stocks.get_by_ticker(ticker)
        if not stock:
            raise StockNotFoundError()
        raw_meta = stock.crawl_metadata_json
        if not isinstance(raw_meta, dict):
            raise AppError(
                "Mã chưa có crawlMetadata (JSON) — cấu hình url/form trước khi crawl",
                "CRAWL_METADATA_MISSING",
                status_code=400,
            )
        try:
            series = fetch_vietstock_price_series(
                raw_meta,
                cookie=body.cookie,
                request_verification_token=body.request_verification_token,
                extra_form=body.extra_form,
            )
        except ValueError as e:
            raise AppError(str(e), "CRAWL_FETCH_FAILED", status_code=422) from e
        if not series:
            raise AppError(
                "Không trích được dãy nến từ JSON (thử response_path / response_series_keys)",
                "CRAWL_EMPTY_SERIES",
                status_code=422,
            )
        return self._crawler.ingest_price_json(stock, series, crawl_type="vietstock_eod")

    def list_crawl_logs(self, limit: int = 100) -> list[CrawlLog]:
        q = select(CrawlLog).order_by(desc(CrawlLog.created_at)).limit(limit)
        return list(self._db.scalars(q).all())

    def list_analysis_results(self, skip: int = 0, limit: int = 100) -> list[AnalysisResult]:
        return self._analysis.list_all_results(skip=skip, limit=limit)
