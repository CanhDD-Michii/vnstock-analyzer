from app.shared.schemas.common import CamelModel


class CrawlerJobPlaceholder(CamelModel):
    job_id: str | None = None
