from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "VN Stock Analyzer API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "mysql+pymysql://root:root@127.0.0.1:3306/vnstock?charset=utf8mb4"

    cors_origins: str = "http://localhost:3000"

    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Crawler / VietStock (có thể ghi đè qua biến môi trường)
    vietstock_finance_origin: str = "https://finance.vietstock.vn"
    vietstock_list_price_path: str = "/data/GetStockDeal_ListPriceByTimeFrame"
    vietstock_http_timeout_seconds: float = 90.0
    crawl_scheduler_tick_seconds: int = 30
    crawl_log_message_max_chars: int = 2000

    seed_admin_on_startup: bool = False  # bật qua SEED_ADMIN_ON_STARTUP=true
    admin_email: str = "admin@example.com"
    admin_password: str = "ChangeMe123!"
    admin_full_name: str = "Administrator"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())

    @property
    def vietstock_list_price_url(self) -> str:
        origin = self.vietstock_finance_origin.rstrip("/")
        path = self.vietstock_list_price_path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{origin}{path}"


settings = Settings()
