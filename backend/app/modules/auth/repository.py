from sqlalchemy.orm import Session


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self._db = db
