from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.db.models import User
from app.modules.admin.schemas import (
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
    ins, upd = AdminService(db).trigger_price_crawl(ticker, body.data)
    return ApiSuccessResponse(
        data=CrawlTriggerResponse(inserted=ins, updated=upd, message="OK"),
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
    ins, upd = AdminService(db).trigger_vietstock_crawl(ticker, body)
    return ApiSuccessResponse(
        data=CrawlTriggerResponse(inserted=ins, updated=upd, message="OK"),
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
