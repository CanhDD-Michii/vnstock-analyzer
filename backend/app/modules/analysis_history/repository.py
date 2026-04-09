from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import AnalysisRequest, AnalysisResult


class AnalysisHistoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_request(
        self,
        *,
        user_id: int,
        stock_id: int,
        request_type: str,
        status: str,
    ) -> AnalysisRequest:
        r = AnalysisRequest(
            user_id=user_id,
            stock_id=stock_id,
            request_type=request_type,
            status=status,
        )
        self._db.add(r)
        self._db.commit()
        self._db.refresh(r)
        return r

    def update_request_status(self, req: AnalysisRequest, status: str) -> None:
        req.status = status
        self._db.commit()

    def create_result(self, **kwargs: Any) -> AnalysisResult:
        res = AnalysisResult(**kwargs)
        self._db.add(res)
        self._db.commit()
        self._db.refresh(res)
        return res

    def list_for_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[AnalysisResult]:
        q = (
            select(AnalysisResult)
            .where(AnalysisResult.user_id == user_id)
            .order_by(desc(AnalysisResult.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(self._db.scalars(q).all())

    def get_result(self, result_id: int, user_id: int) -> AnalysisResult | None:
        return self._db.scalar(
            select(AnalysisResult).where(
                AnalysisResult.id == result_id,
                AnalysisResult.user_id == user_id,
            )
        )

    def list_all_results(self, skip: int = 0, limit: int = 100) -> list[AnalysisResult]:
        q = (
            select(AnalysisResult)
            .order_by(desc(AnalysisResult.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(self._db.scalars(q).all())
