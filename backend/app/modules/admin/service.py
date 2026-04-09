from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppError, StockNotFoundError
from app.db.models import (
    AnalysisResult,
    CrawlLog,
    CrawlSchedule,
    Stock,
    StockPriceHistory,
    User,
    UserRole,
    UserStatus,
)
from app.modules.analysis_history.repository import AnalysisHistoryRepository
from app.modules.admin.schemas import (
    CrawlScheduleUpsertBody,
    StockCreateBody,
    StockPatchBody,
    UserPatchBody,
    VietstockCrawlBody,
)
from app.modules.crawler.dates import today_vn
from app.modules.crawler.service import CrawlerService
from app.modules.crawler.vietstock_client import fetch_vietstock_list_price_backward
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

    def trigger_price_crawl(self, ticker: str, items: list[dict[str, Any]]) -> tuple[int, int, int]:
        stock = self._stocks.get_by_ticker(ticker)
        if not stock:
            raise StockNotFoundError()
        return self._crawler.ingest_price_json(stock, items)

    def _resolve_initial_to_date(self, stock_id: int, metadata: dict[str, Any]) -> date:
        strat = metadata.get("crawl_strategy")
        if not isinstance(strat, dict):
            strat = {}
        mode = strat.get("initial_to_date", "today")
        if mode != "oldest_in_db_minus_1":
            return today_vn()
        min_d = self._db.scalar(
            select(func.min(StockPriceHistory.trading_date)).where(
                StockPriceHistory.stock_id == stock_id
            )
        )
        if min_d is None:
            return today_vn()
        return min_d - timedelta(days=1)

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

    def trigger_vietstock_crawl(self, ticker: str, body: VietstockCrawlBody) -> tuple[int, int, int]:
        stock = self._stocks.get_by_ticker(ticker)
        if not stock:
            raise StockNotFoundError()
        raw_meta = stock.crawl_metadata_json
        if not isinstance(raw_meta, dict):
            # Không bắt buộc lưu metadata trên mã: dùng mặc định (URL ListPrice, form/strategy trong vietstock_client).
            raw_meta = {}
        session_day = today_vn()
        initial = self._resolve_initial_to_date(stock.id, raw_meta)
        try:
            series = fetch_vietstock_list_price_backward(
                raw_meta,
                stock.ticker,
                cookie=body.cookie,
                request_verification_token=body.request_verification_token,
                extra_form=body.extra_form,
                initial_to_date=initial,
            )
        except ValueError as e:
            raise AppError(str(e), "CRAWL_FETCH_FAILED", status_code=422) from e
        if not series:
            raise AppError(
                "GetStockDeal_ListPriceByTimeFrame không trả bản ghi (url, cookie, token, mã)",
                "CRAWL_EMPTY_SERIES",
                status_code=422,
            )
        return self._crawler.ingest_price_json(
            stock,
            series,
            crawl_type="vietstock_list_price",
            skip_locked_historical=True,
            price_session_date=session_day,
        )

    def list_crawl_logs(self, limit: int = 100) -> list[CrawlLog]:
        q = select(CrawlLog).order_by(desc(CrawlLog.created_at)).limit(limit)
        return list(self._db.scalars(q).all())

    def list_crawl_schedules(self) -> list[CrawlSchedule]:
        q = (
            select(CrawlSchedule)
            .options(joinedload(CrawlSchedule.stock))
            .join(Stock, CrawlSchedule.stock_id == Stock.id)
            .order_by(Stock.ticker)
        )
        return list(self._db.scalars(q).unique().all())

    def upsert_crawl_schedule(self, ticker: str, body: CrawlScheduleUpsertBody) -> CrawlSchedule:
        t = ticker.strip().upper()
        stock = self._stocks.get_by_ticker(t)
        if not stock:
            raise StockNotFoundError()
        sched = self._db.scalar(select(CrawlSchedule).where(CrawlSchedule.stock_id == stock.id))
        now = datetime.now(timezone.utc)
        interval_changed = False

        if sched is None:
            if body.interval_minutes is None:
                raise AppError(
                    "intervalMinutes bắt buộc khi tạo lịch crawl mới",
                    "SCHEDULE_INTERVAL_REQUIRED",
                    status_code=400,
                )
            enabled = body.is_enabled if body.is_enabled is not None else True
            sched = CrawlSchedule(
                stock_id=stock.id,
                interval_minutes=body.interval_minutes,
                is_enabled=enabled,
                next_run_at=(
                    now + timedelta(minutes=body.interval_minutes) if enabled else None
                ),
            )
            self._db.add(sched)
            self._db.flush()
        else:
            if "interval_minutes" in body.model_fields_set and body.interval_minutes is not None:
                if body.interval_minutes != sched.interval_minutes:
                    interval_changed = True
                sched.interval_minutes = body.interval_minutes
            if "is_enabled" in body.model_fields_set and body.is_enabled is not None:
                sched.is_enabled = body.is_enabled
                if body.is_enabled and sched.next_run_at is None:
                    sched.next_run_at = now + timedelta(minutes=sched.interval_minutes)

        if "vietstock_cookie" in body.model_fields_set:
            c = body.vietstock_cookie
            sched.vietstock_cookie = (c.strip() or None) if isinstance(c, str) else None
        if "request_verification_token" in body.model_fields_set:
            tok = body.request_verification_token
            sched.request_verification_token = (tok.strip() or None) if isinstance(tok, str) else None

        if interval_changed:
            sched.next_run_at = now + timedelta(minutes=sched.interval_minutes)

        if sched.is_enabled and sched.next_run_at is None:
            sched.next_run_at = now + timedelta(minutes=sched.interval_minutes)

        self._db.commit()
        self._db.refresh(sched)
        return sched

    def delete_crawl_schedule(self, ticker: str) -> None:
        t = ticker.strip().upper()
        stock = self._stocks.get_by_ticker(t)
        if not stock:
            raise StockNotFoundError()
        sched = self._db.scalar(select(CrawlSchedule).where(CrawlSchedule.stock_id == stock.id))
        if sched:
            self._db.delete(sched)
            self._db.commit()

    def list_analysis_results(self, skip: int = 0, limit: int = 100) -> list[AnalysisResult]:
        return self._analysis.list_all_results(skip=skip, limit=limit)
