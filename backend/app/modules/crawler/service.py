from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CrawlLog, Stock, StockPriceHistory
from app.modules.crawler.parser import normalize_price_row


class CrawlerService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def ingest_price_json(
        self,
        stock: Stock,
        items: list[dict[str, Any]],
        *,
        crawl_type: str = "price_json",
    ) -> tuple[int, int]:
        started = datetime.now(timezone.utc)
        log = CrawlLog(
            stock_id=stock.id,
            crawl_type=crawl_type,
            status="running",
            message=None,
            started_at=started,
            finished_at=None,
        )
        self._db.add(log)
        self._db.commit()
        self._db.refresh(log)
        log_id = log.id
        inserted = 0
        updated = 0
        try:
            for raw in items:
                row = normalize_price_row(raw)
                existing = self._db.scalar(
                    select(StockPriceHistory).where(
                        StockPriceHistory.stock_id == stock.id,
                        StockPriceHistory.trading_date == row["trading_date"],
                    )
                )
                if existing:
                    existing.open_price = row["open_price"]
                    existing.high_price = row["high_price"]
                    existing.low_price = row["low_price"]
                    existing.close_price = row["close_price"]
                    existing.price_change = row["price_change"]
                    existing.percent_change = row["percent_change"]
                    existing.total_volume = row["total_volume"]
                    existing.raw_payload_json = row.get("raw_payload_json")
                    updated += 1
                else:
                    self._db.add(
                        StockPriceHistory(
                            stock_id=stock.id,
                            trading_date=row["trading_date"],
                            open_price=row["open_price"],
                            high_price=row["high_price"],
                            low_price=row["low_price"],
                            close_price=row["close_price"],
                            price_change=row["price_change"],
                            percent_change=row["percent_change"],
                            total_volume=row["total_volume"],
                            raw_payload_json=row.get("raw_payload_json"),
                        )
                    )
                    inserted += 1
            self._db.commit()
        except Exception as exc:
            self._db.rollback()
            lg = self._db.get(CrawlLog, log_id)
            if lg:
                lg.status = "failed"
                lg.message = str(exc)[:2000]
                lg.finished_at = datetime.now(timezone.utc)
                self._db.commit()
            raise

        lg = self._db.get(CrawlLog, log_id)
        if lg:
            lg.status = "success"
            lg.message = f"inserted={inserted}, updated={updated}"
            lg.finished_at = datetime.now(timezone.utc)
            self._db.commit()
        return inserted, updated
