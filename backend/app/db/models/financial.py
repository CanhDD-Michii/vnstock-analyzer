from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StockFinancialReport(Base):
    __tablename__ = "stock_financial_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    report_type: Mapped[str] = mapped_column(String(64), default="annual", nullable=False)
    fiscal_year: Mapped[int | None] = mapped_column(nullable=True)
    fiscal_quarter: Mapped[int | None] = mapped_column(nullable=True)
    revenue: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    gross_profit: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    operating_profit: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    net_profit: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    eps: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    bvps: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    total_assets: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    total_liabilities: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    equity: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    operating_cash_flow: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    free_cash_flow: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    raw_payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    stock: Mapped["Stock"] = relationship("Stock", back_populates="financial_reports")
