from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.shared.schemas.common import CamelModel


class AnalysisHistoryItemResponse(CamelModel):
    id: int
    stock_ticker: str
    analysis_date: date
    fundamental_score: int | None
    technical_score: int | None
    risk_score: int | None
    ai_recommendation: str | None
    created_at: datetime


class AnalysisDetailResponse(CamelModel):
    id: int
    stock_ticker: str
    analysis_date: date
    fundamental_score: int | None
    technical_score: int | None
    risk_score: int | None
    ai_summary: str | None
    ai_fundamental_analysis: str | None
    ai_technical_analysis: str | None
    ai_risks_json: list[Any] | None
    ai_conclusion: str | None
    ai_recommendation: str | None
    engine_output_json: dict[str, Any] | None
    raw_ai_response_json: dict[str, Any] | None
    created_at: datetime


class RunAnalysisResponse(CamelModel):
    result_id: int
    engine: dict[str, Any]
    ai: dict[str, Any]
