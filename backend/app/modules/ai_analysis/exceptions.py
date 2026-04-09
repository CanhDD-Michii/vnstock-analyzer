from app.core.exceptions import AppError


class OpenAIResponseFormatError(AppError):
    def __init__(self, message: str = "Invalid OpenAI response format") -> None:
        super().__init__(message, "OPENAI_RESPONSE_FORMAT_ERROR", status_code=502)
