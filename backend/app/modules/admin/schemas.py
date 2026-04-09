from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, Field

from app.shared.schemas.common import CamelModel


class IngestPricePayload(CamelModel):
    data: list[dict[str, Any]] = Field(default_factory=list)


class CrawlTriggerResponse(CamelModel):
    inserted: int
    updated: int
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
