"""Luồng nền: chạy crawl VietStock theo bảng crawl_schedules."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import CrawlSchedule, Stock
from app.db.session import SessionLocal
from app.modules.admin.schemas import VietstockCrawlBody
from app.modules.admin.service import AdminService

logger = get_logger(__name__)

_stop = threading.Event()
_thread: threading.Thread | None = None


def start_crawl_scheduler() -> None:
    global _thread
    if _thread is not None and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_run_loop, name="crawl-scheduler", daemon=True)
    _thread.start()
    logger.info(
        "Crawl scheduler started (tick=%ss)",
        settings.crawl_scheduler_tick_seconds,
    )


def stop_crawl_scheduler() -> None:
    _stop.set()
    logger.info("Crawl scheduler stop requested")


def _run_loop() -> None:
    while not _stop.wait(settings.crawl_scheduler_tick_seconds):
        try:
            _tick()
        except Exception:
            logger.exception("crawl scheduler tick failed")


def _tick() -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        rows = db.scalars(
            select(CrawlSchedule)
            .where(
                CrawlSchedule.is_enabled.is_(True),
                CrawlSchedule.next_run_at.is_not(None),
                CrawlSchedule.next_run_at <= now,
            )
        ).all()
        if not rows:
            return
        svc = AdminService(db)
        for sched in rows:
            stock = db.get(Stock, sched.stock_id)
            if not stock:
                continue
            ticker = stock.ticker
            cookie = (sched.vietstock_cookie or "").strip() or None
            token = (sched.request_verification_token or "").strip() or None
            try:
                ins, upd, sk = svc.trigger_vietstock_crawl(
                    ticker,
                    VietstockCrawlBody(cookie=cookie, request_verification_token=token),
                )
                sched.last_run_status = "success"
                sched.last_run_message = f"inserted={ins}, updated={upd}, skipped={sk}"
            except Exception as e:
                logger.warning("Scheduled crawl failed ticker=%s: %s", ticker, e)
                sched.last_run_status = "failed"
                sched.last_run_message = str(e)[: settings.crawl_log_message_max_chars]
            sched.last_run_at = now
            sched.next_run_at = now + timedelta(minutes=max(1, sched.interval_minutes))
            db.commit()
