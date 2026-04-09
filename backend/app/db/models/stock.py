from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    exchange: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    sector: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    crawl_metadata_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    price_histories: Mapped[list["StockPriceHistory"]] = relationship(
        "StockPriceHistory",
        back_populates="stock",
        cascade="all, delete-orphan",
        order_by="StockPriceHistory.trading_date",
    )
    financial_reports: Mapped[list["StockFinancialReport"]] = relationship(
        "StockFinancialReport",
        back_populates="stock",
        cascade="all, delete-orphan",
    )
    key_metrics: Mapped[list["StockKeyMetrics"]] = relationship(
        "StockKeyMetrics",
        back_populates="stock",
        cascade="all, delete-orphan",
    )
    technical_indicators: Mapped[list["StockTechnicalIndicator"]] = relationship(
        "StockTechnicalIndicator",
        back_populates="stock",
        cascade="all, delete-orphan",
    )
    analysis_requests: Mapped[list["AnalysisRequest"]] = relationship(
        "AnalysisRequest",
        back_populates="stock",
        cascade="all, delete-orphan",
    )
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="stock",
        cascade="all, delete-orphan",
    )
    crawl_logs: Mapped[list["CrawlLog"]] = relationship(
        "CrawlLog",
        back_populates="stock",
        cascade="all, delete-orphan",
    )
