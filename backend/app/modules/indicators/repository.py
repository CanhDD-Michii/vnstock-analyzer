from sqlalchemy.orm import Session


class IndicatorRepository:
    def __init__(self, db: Session) -> None:
        self._db = db
