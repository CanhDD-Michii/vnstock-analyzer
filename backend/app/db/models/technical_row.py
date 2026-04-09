from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StockTechnicalIndicator(Base):
    __tablename__ = "stock_technical_indicators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    indicator_date: Mapped[date] = mapped_column(Date, nullable=False)
    sma_20: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    sma_50: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    sma_200: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    ema_12: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    ema_26: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    macd: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    macd_signal: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    macd_histogram: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    rsi_14: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    bollinger_upper: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    bollinger_middle: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    bollinger_lower: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    atr_14: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    obv: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    volume_ma_20: Mapped[float | None] = mapped_column(Numeric(24, 4), nullable=True)
    drawdown_52w: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    volatility_30d: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    stock: Mapped["Stock"] = relationship("Stock", back_populates="technical_indicators")
