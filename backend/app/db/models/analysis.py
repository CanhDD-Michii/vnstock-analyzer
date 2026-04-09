from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    request_type: Mapped[str] = mapped_column(String(64), default="full", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="analysis_requests")
    stock: Mapped["Stock"] = relationship("Stock", back_populates="analysis_requests")
    results: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="request",
        cascade="all, delete-orphan",
    )


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    analysis_request_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_requests.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    snapshot_price: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    snapshot_volume: Mapped[int | None] = mapped_column(nullable=True)
    snapshot_pe: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    snapshot_pb: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    snapshot_roe: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    snapshot_rsi: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    snapshot_macd: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    fundamental_score: Mapped[int | None] = mapped_column(nullable=True)
    technical_score: Mapped[int | None] = mapped_column(nullable=True)
    risk_score: Mapped[int | None] = mapped_column(nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_fundamental_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_technical_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_risks_json: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    ai_conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(String(32), nullable=True)
    raw_ai_response_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    engine_output_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    request: Mapped["AnalysisRequest"] = relationship(
        "AnalysisRequest", back_populates="results"
    )
    user: Mapped["User"] = relationship("User", back_populates="analysis_results")
    stock: Mapped["Stock"] = relationship("Stock", back_populates="analysis_results", lazy="joined")
