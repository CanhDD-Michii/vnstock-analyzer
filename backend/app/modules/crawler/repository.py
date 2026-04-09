from sqlalchemy.orm import Session


class CrawlerRepository:
    def __init__(self, db: Session) -> None:
        self._db = db
