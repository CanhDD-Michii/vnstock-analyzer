from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.models import User
from app.modules.analysis_history.repository import AnalysisHistoryRepository
from app.modules.analysis_history.schemas import AnalysisDetailResponse, AnalysisHistoryItemResponse
from app.modules.analysis_history.service import AnalysisHistoryService


class AnalysisHistoryReadService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AnalysisHistoryRepository(db)

    def list_history(self, user: User, skip: int, limit: int) -> list[AnalysisHistoryItemResponse]:
        rows = self._repo.list_for_user(user.id, skip=skip, limit=limit)
        out: list[AnalysisHistoryItemResponse] = []
        for r in rows:
            ticker = r.stock.ticker if r.stock else ""
            out.append(
                AnalysisHistoryItemResponse(
                    id=r.id,
                    stock_ticker=ticker,
                    analysis_date=r.analysis_date,
                    fundamental_score=r.fundamental_score,
                    technical_score=r.technical_score,
                    risk_score=r.risk_score,
                    ai_recommendation=r.ai_recommendation,
                    created_at=r.created_at,
                )
            )
        return out

    def get_detail(self, user: User, result_id: int) -> AnalysisDetailResponse:
        r = self._repo.get_result(result_id, user.id)
        if not r:
            raise AppError("Không tìm thấy kết quả", "ANALYSIS_NOT_FOUND", status_code=404)
        ticker = r.stock.ticker if r.stock else ""
        return AnalysisDetailResponse(
            id=r.id,
            stock_ticker=ticker,
            analysis_date=r.analysis_date,
            fundamental_score=r.fundamental_score,
            technical_score=r.technical_score,
            risk_score=r.risk_score,
            ai_summary=r.ai_summary,
            ai_fundamental_analysis=r.ai_fundamental_analysis,
            ai_technical_analysis=r.ai_technical_analysis,
            ai_risks_json=r.ai_risks_json,
            ai_conclusion=r.ai_conclusion,
            ai_recommendation=r.ai_recommendation,
            engine_output_json=r.engine_output_json,
            raw_ai_response_json=r.raw_ai_response_json,
            created_at=r.created_at,
        )


def get_analysis_runner(db: Session) -> AnalysisHistoryService:
    return AnalysisHistoryService(db)
