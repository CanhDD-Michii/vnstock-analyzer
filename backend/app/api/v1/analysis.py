from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.modules.analysis_history.history_service import AnalysisHistoryReadService, get_analysis_runner
from app.modules.analysis_history.schemas import (
    AnalysisDetailResponse,
    AnalysisHistoryItemResponse,
    RunAnalysisResponse,
)
from app.shared.schemas.common import ApiSuccessResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{ticker}", response_model=ApiSuccessResponse[RunAnalysisResponse])
def run_analysis(
    ticker: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[RunAnalysisResponse]:
    raw = get_analysis_runner(db).run_analysis_for_ticker(user, ticker)
    data = RunAnalysisResponse(
        result_id=raw["result_id"],
        engine=raw["engine"],
        ai=raw["ai"],
    )
    return ApiSuccessResponse(data=data, message="Phân tích hoàn tất")


@router.get("/history", response_model=ApiSuccessResponse[list[AnalysisHistoryItemResponse]])
def list_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> ApiSuccessResponse[list[AnalysisHistoryItemResponse]]:
    data = AnalysisHistoryReadService(db).list_history(user, skip=skip, limit=limit)
    return ApiSuccessResponse(data=data, message="Success")


@router.get(
    "/history/{result_id}",
    response_model=ApiSuccessResponse[AnalysisDetailResponse],
)
def get_history_detail(
    result_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiSuccessResponse[AnalysisDetailResponse]:
    data = AnalysisHistoryReadService(db).get_detail(user, result_id)
    return ApiSuccessResponse(data=data, message="Success")
