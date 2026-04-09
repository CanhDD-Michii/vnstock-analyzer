from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StockKeyMetrics(Base):
    __tablename__ = "stock_key_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    pe: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    pb: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    roe: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    roa: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    gross_margin: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    net_margin: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    debt_to_equity: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    current_ratio: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    quick_ratio: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    revenue_growth_yoy: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    profit_growth_yoy: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    eps_growth_yoy: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    stock: Mapped["Stock"] = relationship("Stock", back_populates="key_metrics")
