class AppError(Exception):
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class StockNotFoundError(AppError):
    def __init__(self, message: str = "Stock not found") -> None:
        super().__init__(message, "STOCK_NOT_FOUND", status_code=404)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, "UNAUTHORIZED", status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, "FORBIDDEN", status_code=403)
