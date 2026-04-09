from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_stocks_crawl_metadata_column() -> None:
    """Thêm cột khi DB đã tồn tại trước khi có trường này (create_all không ALTER)."""
    insp = inspect(engine)
    if "stocks" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("stocks")}
    if "crawl_metadata_json" in cols:
        return
    dialect = engine.dialect.name
    if dialect == "mysql":
        stmt = "ALTER TABLE stocks ADD COLUMN crawl_metadata_json JSON NULL"
    elif dialect == "sqlite":
        stmt = "ALTER TABLE stocks ADD COLUMN crawl_metadata_json TEXT NULL"
    else:
        stmt = "ALTER TABLE stocks ADD COLUMN crawl_metadata_json JSONB NULL"
    try:
        with engine.begin() as conn:
            conn.execute(text(stmt))
    except OperationalError:
        pass


def init_db_schema() -> None:
    """Gọi sau khi đã định nghĩa models — khung chưa tạo bảng cụ thể."""
    Base.metadata.create_all(bind=engine)
    _ensure_stocks_crawl_metadata_column()
