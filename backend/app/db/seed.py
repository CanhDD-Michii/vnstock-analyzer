from __future__ import annotations

import random
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.models import (
    AiPromptConfig,
    Stock,
    StockPriceHistory,
    User,
    UserRole,
    UserStatus,
)
from app.modules.ai_analysis.prompt_builder import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_TEMPLATE,
)


def seed_prompt_config(db: Session) -> None:
    existing = db.scalar(select(AiPromptConfig).where(AiPromptConfig.name == "stock_analysis_v1"))
    if existing:
        return
    db.add(
        AiPromptConfig(
            name="stock_analysis_v1",
            prompt_type="stock_analysis",
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            user_prompt_template=DEFAULT_USER_TEMPLATE,
            is_active=True,
            version=1,
        )
    )
    db.commit()


def seed_admin_and_demo(db: Session) -> None:
    if not settings.seed_admin_on_startup:
        return
    email = settings.admin_email.lower()
    if db.scalar(select(User).where(User.email == email)):
        return
    admin = User(
        full_name=settings.admin_full_name,
        email=email,
        password_hash=hash_password(settings.admin_password),
        role=UserRole.admin.value,
        status=UserStatus.active.value,
    )
    db.add(admin)
    db.commit()


def seed_demo_stock_if_empty(db: Session) -> None:
    ticker = "FPT"
    if db.scalar(select(Stock).where(Stock.ticker == ticker)):
        return
    stock = Stock(
        ticker=ticker,
        company_name="FPT Corporation",
        exchange="HOSE",
        sector="Technology",
        description="Dữ liệu demo tổng hợp để chạy engine.",
        is_active=True,
    )
    db.add(stock)
    db.flush()
    price = 100.0
    rows: list[StockPriceHistory] = []
    start = date.today() - timedelta(days=300)
    for i in range(220):
        d = start + timedelta(days=i)
        drift = random.uniform(-0.8, 0.9)
        price = max(10.0, price * (1 + drift / 100))
        o = price * random.uniform(0.995, 1.005)
        c = price * random.uniform(0.995, 1.005)
        h = max(o, c) * random.uniform(1.0, 1.012)
        l = min(o, c) * random.uniform(0.988, 1.0)
        vol = random.randint(800_000, 3_000_000)
        ch = c - o
        pct = (ch / o * 100) if o else 0
        rows.append(
            StockPriceHistory(
                stock_id=stock.id,
                trading_date=d,
                open_price=round(o, 4),
                high_price=round(h, 4),
                low_price=round(l, 4),
                close_price=round(c, 4),
                price_change=round(ch, 4),
                percent_change=round(pct, 4),
                total_volume=vol,
                raw_payload_json=None,
            )
        )
    db.add_all(rows)
    db.commit()


def run_all_seeds(db: Session) -> None:
    seed_prompt_config(db)
    seed_admin_and_demo(db)
    seed_demo_stock_if_empty(db)
