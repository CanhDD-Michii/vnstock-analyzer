from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class ApiSuccessResponse(CamelModel, Generic[T]):
    data: T
    message: str = "Success"


class ApiErrorBody(CamelModel):
    message: str
    error_code: str


class HealthData(CamelModel):
    status: str = "ok"


class PlaceholderData(CamelModel):
    """Payload rỗng cho endpoint chưa triển khai."""

    placeholder: bool = True
