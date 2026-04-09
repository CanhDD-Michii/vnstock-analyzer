from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, StockNotFoundError
from app.modules.indicators.pipeline import MIN_BARS, run_indicator_engine
from app.modules.stocks.performance import compute_performance_from_bars
from app.modules.stocks.repository import StockRepository
from app.modules.stocks.schemas import (
    KeyMetricsResponse,
    PriceBarResponse,
    StockDetailResponse,
    StockListItemResponse,
    StockPerformanceRowResponse,
)


class StockService:
    def __init__(self, db: Session) -> None:
        self._repo = StockRepository(db)

    def list_stocks(self, skip: int = 0, limit: int = 100) -> list[StockListItemResponse]:
        return [
            StockListItemResponse(
                id=s.id,
                ticker=s.ticker,
                company_name=s.company_name,
                exchange=s.exchange,
                sector=s.sector,
                is_active=s.is_active,
            )
            for s in self._repo.list_active(skip=skip, limit=limit)
        ]

    def list_performance_board(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        price_limit: int = 800,
    ) -> list[StockPerformanceRowResponse]:
        rows_out: list[StockPerformanceRowResponse] = []
        for s in self._repo.list_active(skip=skip, limit=limit):
            hist = self._repo.get_price_rows_asc(s.id, limit=price_limit)
            bars = [self._repo.price_row_to_bar(r) for r in hist]
            p = compute_performance_from_bars(bars)
            rows_out.append(
                StockPerformanceRowResponse(
                    ticker=s.ticker,
                    company_name=s.company_name,
                    as_of_date=p["as_of_date"],
                    close_price=p["close_price"],
                    pct_day=p["pct_day"],
                    pct_week=p["pct_week"],
                    pct_month=p["pct_month"],
                    pct_quarter=p["pct_quarter"],
                    pct_ytd=p["pct_ytd"],
                    pct_year=p["pct_year"],
                )
            )
        return rows_out

    def get_detail(self, ticker: str) -> StockDetailResponse:
        s = self._repo.get_by_ticker(ticker)
        if not s:
            raise StockNotFoundError()
        return StockDetailResponse(
            id=s.id,
            ticker=s.ticker,
            company_name=s.company_name,
            exchange=s.exchange,
            sector=s.sector,
            description=s.description,
            is_active=s.is_active,
        )

    def get_prices(self, ticker: str, limit: int = 500) -> list[PriceBarResponse]:
        s = self._repo.get_by_ticker(ticker)
        if not s:
            raise StockNotFoundError()
        rows = self._repo.get_price_rows_asc(s.id, limit=limit)
        return [
            PriceBarResponse(
                trading_date=r.trading_date,
                open_price=float(r.open_price),
                high_price=float(r.high_price),
                low_price=float(r.low_price),
                close_price=float(r.close_price),
                total_volume=int(r.total_volume),
            )
            for r in rows
        ]

    def get_metrics(self, ticker: str) -> KeyMetricsResponse | None:
        s = self._repo.get_by_ticker(ticker)
        if not s:
            raise StockNotFoundError()
        m = self._repo.get_latest_metrics(s.id)
        if not m:
            return None
        d = self._repo.metrics_to_dict(m)
        return KeyMetricsResponse(
            metric_date=m.metric_date,
            pe=d.get("pe"),
            pb=d.get("pb"),
            roe=d.get("roe"),
            roa=d.get("roa"),
            gross_margin=d.get("gross_margin"),
            net_margin=d.get("net_margin"),
            debt_to_equity=d.get("debt_to_equity"),
            revenue_growth_yoy=d.get("revenue_growth_yoy"),
            profit_growth_yoy=d.get("profit_growth_yoy"),
        )

    def get_technicals(self, ticker: str) -> dict[str, Any]:
        s = self._repo.get_by_ticker(ticker)
        if not s:
            raise StockNotFoundError()
        bars = [self._repo.price_row_to_bar(r) for r in self._repo.get_price_rows_asc(s.id)]
        if len(bars) < MIN_BARS:
            raise AppError(
                f"Cần tối thiểu {MIN_BARS} phiên giá để tính chỉ báo",
                "INSUFFICIENT_PRICE_HISTORY",
            )
        engine = run_indicator_engine(bars, s.ticker)
        return {
            "analysis_date": engine["analysis_date"],
            "technical_score": engine["technical_score"],
            "indicators": engine["indicators"],
            "scores": engine["scores"],
            "state": engine["state"],
            "levels": engine["levels"],
            "active_strategies": engine["active_strategies"],
            "risk": engine["risk"],
            "latest_price": engine["latest_price"],
        }
