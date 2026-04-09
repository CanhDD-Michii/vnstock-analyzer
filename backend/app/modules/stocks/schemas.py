from __future__ import annotations

from datetime import date

from app.shared.schemas.common import CamelModel


class StockListItemResponse(CamelModel):
    id: int
    ticker: str
    company_name: str
    exchange: str
    sector: str
    is_active: bool


class StockDetailResponse(CamelModel):
    id: int
    ticker: str
    company_name: str
    exchange: str
    sector: str
    description: str | None
    is_active: bool


class PriceBarResponse(CamelModel):
    trading_date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    total_volume: int


class KeyMetricsResponse(CamelModel):
    metric_date: date | None
    pe: float | None
    pb: float | None
    roe: float | None
    roa: float | None
    gross_margin: float | None
    net_margin: float | None
    debt_to_equity: float | None
    revenue_growth_yoy: float | None
    profit_growth_yoy: float | None


class TechnicalSnapshotResponse(CamelModel):
    """Snapshot chỉ báo mới nhất (tính runtime từ giá lịch sử)."""

    model_config = {"extra": "allow"}
