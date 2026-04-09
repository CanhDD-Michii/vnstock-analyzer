from app.core.exceptions import AppError


class InvalidCredentialsError(AppError):
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message, "INVALID_CREDENTIALS")
