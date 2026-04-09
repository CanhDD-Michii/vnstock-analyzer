from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CrawlLog, Stock, StockPriceHistory
from app.modules.crawler.dates import today_vn
from app.modules.crawler.parser import normalize_price_row


def _num_eq(a: object, b: object) -> bool:
    try:
        return float(a) == float(b)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return a == b


def _price_row_unchanged(existing: StockPriceHistory, row: dict[str, Any]) -> bool:
    return (
        _num_eq(existing.open_price, row["open_price"])
        and _num_eq(existing.high_price, row["high_price"])
        and _num_eq(existing.low_price, row["low_price"])
        and _num_eq(existing.close_price, row["close_price"])
        and _num_eq(existing.price_change or 0, row.get("price_change") or 0)
        and _num_eq(existing.percent_change or 0, row.get("percent_change") or 0)
        and int(existing.total_volume) == int(row.get("total_volume") or 0)
    )


class CrawlerService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def ingest_price_json(
        self,
        stock: Stock,
        items: list[dict[str, Any]],
        *,
        crawl_type: str = "price_json",
        skip_locked_historical: bool = False,
        price_session_date: date | None = None,
    ) -> tuple[int, int, int]:
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
        skipped = 0
        session_day = price_session_date if price_session_date is not None else today_vn()
        try:
            for raw in items:
                row = normalize_price_row(raw)
                td = row["trading_date"]
                existing = self._db.scalar(
                    select(StockPriceHistory).where(
                        StockPriceHistory.stock_id == stock.id,
                        StockPriceHistory.trading_date == td,
                    )
                )
                if existing and skip_locked_historical and td != session_day:
                    skipped += 1
                    continue
                if existing:
                    if _price_row_unchanged(existing, row):
                        skipped += 1
                        continue
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
                            trading_date=td,
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
            lg.message = f"inserted={inserted}, updated={updated}, skipped={skipped}"
            lg.finished_at = datetime.now(timezone.utc)
            self._db.commit()
        return inserted, updated, skipped
