from sqlalchemy.orm import Session

from app.modules.ai_analysis.repository import AiAnalysisRepository


class AiAnalysisService:
    def __init__(self, db: Session) -> None:
        self._repo = AiAnalysisRepository(db)
