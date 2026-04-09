from sqlalchemy.orm import Session


class AdminRepository:
    def __init__(self, db: Session) -> None:
        self._db = db
