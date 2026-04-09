from sqlalchemy.orm import Session


class AiAnalysisRepository:
    def __init__(self, db: Session) -> None:
        self._db = db
