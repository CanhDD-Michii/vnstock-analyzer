from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, Field

from app.shared.schemas.common import CamelModel


class IngestPricePayload(CamelModel):
    data: list[dict[str, Any]] = Field(default_factory=list)


class CrawlTriggerResponse(CamelModel):
    inserted: int
    updated: int
    skipped: int = 0
    message: str | None = None


class StockCreateBody(CamelModel):
    ticker: str
    company_name: str
    exchange: str = ""
    sector: str = ""
    description: str | None = None
    crawl_metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("crawlMetadata", "crawl_metadata"),
    )


class StockPatchBody(CamelModel):
    company_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("companyName", "company_name"),
    )
    crawl_metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("crawlMetadata", "crawl_metadata"),
    )


class UserPatchBody(CamelModel):
    full_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("fullName", "full_name"),
    )
    role: Literal["user", "admin"] | None = None
    status: Literal["active", "inactive"] | None = None


class CrawlScheduleUpsertBody(CamelModel):
    """Tạo/cập nhật lịch crawl cho một mã."""

    is_enabled: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("isEnabled", "is_enabled"),
    )
    interval_minutes: int | None = Field(
        default=None,
        ge=15,
        le=10080,
        validation_alias=AliasChoices("intervalMinutes", "interval_minutes"),
    )
    vietstock_cookie: str | None = Field(
        default=None,
        validation_alias=AliasChoices("vietstockCookie", "vietstock_cookie"),
    )
    request_verification_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "requestVerificationToken",
            "request_verification_token",
            "__RequestVerificationToken",
        ),
    )


class VietstockCrawlBody(CamelModel):
    cookie: str | None = None
    request_verification_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "__RequestVerificationToken",
            "requestVerificationToken",
            "request_verification_token",
        ),
    )
    extra_form: dict[str, str] | None = Field(
        default=None,
        validation_alias=AliasChoices("extraForm", "extra_form"),
    )
