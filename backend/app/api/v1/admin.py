from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.exceptions import StockNotFoundError
from app.db.models import Stock, User
from app.modules.admin.schemas import (
    CrawlScheduleUpsertBody,
    CrawlTriggerResponse,
    IngestPricePayload,
    StockCreateBody,
    StockPatchBody,
    UserPatchBody,
    VietstockCrawlBody,
)
from app.modules.admin.service import AdminService
from app.shared.schemas.common import CamelModel, ApiSuccessResponse


class UserAdminRow(CamelModel):
    id: int
    full_name: str
    email: str
    role: str
    status: str


class StockAdminRow(CamelModel):
    id: int
    ticker: str
    company_name: str
    exchange: str
    sector: str
    is_active: bool
    crawl_metadata: dict | list | None = None


class CrawlLogRow(CamelModel):
    id: int
    stock_id: int | None
    crawl_type: str
    status: str
    message: str | None
    started_at: str | None
    finished_at: str | None


class CrawlScheduleRow(CamelModel):
    id: int
    stock_id: int
    ticker: str
    company_name: str
    is_enabled: bool
    interval_minutes: int
    next_run_at: str | None
    last_run_at: str | None
    last_run_status: str | None
    last_run_message: str | None
    has_vietstock_cookie: bool
    has_request_verification_token: bool


def _crawl_schedule_row(sched, stock) -> CrawlScheduleRow:
    return CrawlScheduleRow(
        id=sched.id,
        stock_id=sched.stock_id,
        ticker=stock.ticker,
        company_name=stock.company_name,
        is_enabled=sched.is_enabled,
        interval_minutes=sched.interval_minutes,
        next_run_at=sched.next_run_at.isoformat() if sched.next_run_at else None,
        last_run_at=sched.last_run_at.isoformat() if sched.last_run_at else None,
        last_run_status=sched.last_run_status,
        last_run_message=sched.last_run_message,
        has_vietstock_cookie=bool((sched.vietstock_cookie or "").strip()),
        has_request_verification_token=bool((sched.request_verification_token or "").strip()),
    )


class AnalysisAdminRow(CamelModel):
    id: int
    user_id: int
    stock_id: int
    analysis_date: str
    ai_recommendation: str | None
    technical_score: int | None


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=ApiSuccessResponse[list[UserAdminRow]])
def admin_users(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> ApiSuccessResponse[list[UserAdminRow]]:
    users = AdminService(db).list_users(skip=skip, limit=limit)
    data = [
        UserAdminRow(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            role=u.role,
            status=u.status,
        )
        for u in users
    ]
    return ApiSuccessResponse(data=data, message="Success")


@router.patch("/users/{user_id}", response_model=ApiSuccessResponse[UserAdminRow])
def admin_patch_user(
    user_id: int,
    body: UserPatchBody,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[UserAdminRow]:
    u = AdminService(db).patch_user(user_id, body, admin)
    return ApiSuccessResponse(
        data=UserAdminRow(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            role=u.role,
            status=u.status,
        ),
        message="Đã cập nhật người dùng",
    )


@router.get("/stocks", response_model=ApiSuccessResponse[list[StockAdminRow]])
def admin_stocks(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
) -> ApiSuccessResponse[list[StockAdminRow]]:
    stocks = AdminService(db).list_stocks(skip=skip, limit=limit)
    data = [
        StockAdminRow(
            id=s.id,
            ticker=s.ticker,
            company_name=s.company_name,
            exchange=s.exchange,
            sector=s.sector,
            is_active=s.is_active,
            crawl_metadata=s.crawl_metadata_json,
        )
        for s in stocks
    ]
    return ApiSuccessResponse(data=data, message="Success")


@router.post("/stocks", response_model=ApiSuccessResponse[StockAdminRow])
def admin_create_stock(
    body: StockCreateBody,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[StockAdminRow]:
    s = AdminService(db).create_stock(body)
    return ApiSuccessResponse(
        data=StockAdminRow(
            id=s.id,
            ticker=s.ticker,
            company_name=s.company_name,
            exchange=s.exchange,
            sector=s.sector,
            is_active=s.is_active,
            crawl_metadata=s.crawl_metadata_json,
        ),
        message="Đã tạo mã",
    )


@router.patch("/stocks/{ticker}", response_model=ApiSuccessResponse[StockAdminRow])
def admin_patch_stock(
    ticker: str,
    body: StockPatchBody,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[StockAdminRow]:
    s = AdminService(db).patch_stock(ticker, body)
    return ApiSuccessResponse(
        data=StockAdminRow(
            id=s.id,
            ticker=s.ticker,
            company_name=s.company_name,
            exchange=s.exchange,
            sector=s.sector,
            is_active=s.is_active,
            crawl_metadata=s.crawl_metadata_json,
        ),
        message="Đã cập nhật",
    )


@router.post(
    "/crawl/{ticker}",
    response_model=ApiSuccessResponse[CrawlTriggerResponse],
)
def admin_crawl_ticker(
    ticker: str,
    body: IngestPricePayload,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[CrawlTriggerResponse]:
    ins, upd, sk = AdminService(db).trigger_price_crawl(ticker, body.data)
    return ApiSuccessResponse(
        data=CrawlTriggerResponse(inserted=ins, updated=upd, skipped=sk, message="OK"),
        message="Crawl hoàn tất",
    )


@router.post(
    "/crawl/vietstock/{ticker}",
    response_model=ApiSuccessResponse[CrawlTriggerResponse],
)
def admin_crawl_vietstock(
    ticker: str,
    body: VietstockCrawlBody,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[CrawlTriggerResponse]:
    ins, upd, sk = AdminService(db).trigger_vietstock_crawl(ticker, body)
    return ApiSuccessResponse(
        data=CrawlTriggerResponse(inserted=ins, updated=upd, skipped=sk, message="OK"),
        message="Crawl VietStock hoàn tất",
    )


@router.get("/crawl/logs", response_model=ApiSuccessResponse[list[CrawlLogRow]])
def admin_crawl_logs(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
) -> ApiSuccessResponse[list[CrawlLogRow]]:
    logs = AdminService(db).list_crawl_logs(limit=limit)
    data = [
        CrawlLogRow(
            id=lg.id,
            stock_id=lg.stock_id,
            crawl_type=lg.crawl_type,
            status=lg.status,
            message=lg.message,
            started_at=lg.started_at.isoformat() if lg.started_at else None,
            finished_at=lg.finished_at.isoformat() if lg.finished_at else None,
        )
        for lg in logs
    ]
    return ApiSuccessResponse(data=data, message="Success")


@router.get("/crawl/schedules", response_model=ApiSuccessResponse[list[CrawlScheduleRow]])
def admin_list_crawl_schedules(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[list[CrawlScheduleRow]]:
    schedules = AdminService(db).list_crawl_schedules()
    data = [_crawl_schedule_row(s, s.stock) for s in schedules]
    return ApiSuccessResponse(data=data, message="Success")


@router.put("/crawl/schedules/{ticker}", response_model=ApiSuccessResponse[CrawlScheduleRow])
def admin_upsert_crawl_schedule(
    ticker: str,
    body: CrawlScheduleUpsertBody,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[CrawlScheduleRow]:
    sched = AdminService(db).upsert_crawl_schedule(ticker, body)
    stock = db.get(Stock, sched.stock_id)
    if stock is None:
        raise StockNotFoundError()
    return ApiSuccessResponse(
        data=_crawl_schedule_row(sched, stock),
        message="Đã lưu lịch crawl",
    )



class AdminOkBody(CamelModel):
    ok: bool = True


@router.delete("/crawl/schedules/{ticker}", response_model=ApiSuccessResponse[AdminOkBody])
def admin_delete_crawl_schedule(
    ticker: str,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[AdminOkBody]:
    AdminService(db).delete_crawl_schedule(ticker)
    return ApiSuccessResponse(data=AdminOkBody(ok=True), message="Đã xóa lịch crawl")


@router.get("/analysis", response_model=ApiSuccessResponse[list[AnalysisAdminRow]])
def admin_analysis(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> ApiSuccessResponse[list[AnalysisAdminRow]]:
    rows = AdminService(db).list_analysis_results(skip=skip, limit=limit)
    data = [
        AnalysisAdminRow(
            id=r.id,
            user_id=r.user_id,
            stock_id=r.stock_id,
            analysis_date=r.analysis_date.isoformat(),
            ai_recommendation=r.ai_recommendation,
            technical_score=r.technical_score,
        )
        for r in rows
    ]
    return ApiSuccessResponse(data=data, message="Success")
