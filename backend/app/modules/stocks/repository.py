from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import Stock, StockKeyMetrics, StockPriceHistory


class StockRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_active(self, skip: int = 0, limit: int = 100) -> list[Stock]:
        q = (
            select(Stock)
            .where(Stock.is_active.is_(True))
            .order_by(Stock.ticker)
            .offset(skip)
            .limit(limit)
        )
        return list(self._db.scalars(q).all())

    def get_by_ticker(self, ticker: str) -> Stock | None:
        t = ticker.strip().upper()
        return self._db.scalar(select(Stock).where(Stock.ticker == t))

    def get_price_rows_asc(self, stock_id: int, limit: int = 400) -> list[StockPriceHistory]:
        q = (
            select(StockPriceHistory)
            .where(StockPriceHistory.stock_id == stock_id)
            .order_by(desc(StockPriceHistory.trading_date))
            .limit(limit)
        )
        rows = list(self._db.scalars(q).all())
        rows.reverse()
        return rows

    def get_latest_metrics(self, stock_id: int) -> StockKeyMetrics | None:
        q = (
            select(StockKeyMetrics)
            .where(StockKeyMetrics.stock_id == stock_id)
            .order_by(desc(StockKeyMetrics.metric_date))
            .limit(1)
        )
        return self._db.scalar(q)

    def create_stock(
        self,
        *,
        ticker: str,
        company_name: str,
        exchange: str,
        sector: str,
        description: str | None,
        crawl_metadata_json: dict[str, Any] | None = None,
    ) -> Stock:
        s = Stock(
            ticker=ticker.upper(),
            company_name=company_name,
            exchange=exchange,
            sector=sector,
            description=description,
            crawl_metadata_json=crawl_metadata_json,
            is_active=True,
        )
        self._db.add(s)
        self._db.commit()
        self._db.refresh(s)
        return s

    def patch_stock_admin(
        self,
        ticker: str,
        *,
        company_name: str | None = None,
        set_company_name: bool = False,
        crawl_metadata_json: dict[str, Any] | None = None,
        set_crawl_metadata: bool = False,
    ) -> Stock | None:
        s = self.get_by_ticker(ticker)
        if not s:
            return None
        if set_company_name and company_name is not None:
            s.company_name = company_name
        if set_crawl_metadata:
            s.crawl_metadata_json = crawl_metadata_json
        self._db.commit()
        self._db.refresh(s)
        return s

    def metrics_to_dict(self, m: StockKeyMetrics) -> dict[str, Any]:
        return {
            "metric_date": m.metric_date.isoformat(),
            "pe": float(m.pe) if m.pe is not None else None,
            "pb": float(m.pb) if m.pb is not None else None,
            "roe": float(m.roe) if m.roe is not None else None,
            "roa": float(m.roa) if m.roa is not None else None,
            "gross_margin": float(m.gross_margin) if m.gross_margin is not None else None,
            "net_margin": float(m.net_margin) if m.net_margin is not None else None,
            "debt_to_equity": float(m.debt_to_equity) if m.debt_to_equity is not None else None,
            "current_ratio": float(m.current_ratio) if m.current_ratio is not None else None,
            "quick_ratio": float(m.quick_ratio) if m.quick_ratio is not None else None,
            "revenue_growth_yoy": float(m.revenue_growth_yoy)
            if m.revenue_growth_yoy is not None
            else None,
            "profit_growth_yoy": float(m.profit_growth_yoy)
            if m.profit_growth_yoy is not None
            else None,
            "eps_growth_yoy": float(m.eps_growth_yoy) if m.eps_growth_yoy is not None else None,
        }

    def price_row_to_bar(self, r: StockPriceHistory) -> dict[str, Any]:
        return {
            "trading_date": r.trading_date,
            "open_price": float(r.open_price),
            "high_price": float(r.high_price),
            "low_price": float(r.low_price),
            "close_price": float(r.close_price),
            "total_volume": int(r.total_volume),
        }
