from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.modules.stocks.schemas import (
    KeyMetricsResponse,
    PriceBarResponse,
    StockDetailResponse,
    StockListItemResponse,
    StockPerformanceRowResponse,
)
from app.modules.stocks.service import StockService
from app.shared.schemas.common import ApiSuccessResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/", response_model=ApiSuccessResponse[list[StockListItemResponse]])
def list_stocks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[list[StockListItemResponse]]:
    data = StockService(db).list_stocks(skip=skip, limit=limit)
    return ApiSuccessResponse(data=data, message="Success")


@router.get(
    "/performance-board",
    response_model=ApiSuccessResponse[list[StockPerformanceRowResponse]],
)
def list_performance_board(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    price_limit: int = Query(800, ge=50, le=2000),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[list[StockPerformanceRowResponse]]:
    data = StockService(db).list_performance_board(
        skip=skip, limit=limit, price_limit=price_limit
    )
    return ApiSuccessResponse(data=data, message="Success")


@router.get("/{ticker}/prices", response_model=ApiSuccessResponse[list[PriceBarResponse]])
def get_prices(
    ticker: str,
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[list[PriceBarResponse]]:
    data = StockService(db).get_prices(ticker, limit=limit)
    return ApiSuccessResponse(data=data, message="Success")


@router.get(
    "/{ticker}/metrics",
    response_model=ApiSuccessResponse[KeyMetricsResponse | None],
)
def get_metrics(
    ticker: str,
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[KeyMetricsResponse | None]:
    data = StockService(db).get_metrics(ticker)
    return ApiSuccessResponse(data=data, message="Success")


@router.get("/{ticker}/technicals")
def get_technicals(
    ticker: str,
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[dict]:
    data = StockService(db).get_technicals(ticker)
    return ApiSuccessResponse(data=data, message="Success")


@router.get("/{ticker}", response_model=ApiSuccessResponse[StockDetailResponse])
def get_stock(
    ticker: str,
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[StockDetailResponse]:
    data = StockService(db).get_detail(ticker)
    return ApiSuccessResponse(data=data, message="Success")
