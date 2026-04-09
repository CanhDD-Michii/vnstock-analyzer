from sqlalchemy.orm import Session

from app.modules.indicators.repository import IndicatorRepository


class IndicatorService:
    def __init__(self, db: Session) -> None:
        self._repo = IndicatorRepository(db)
