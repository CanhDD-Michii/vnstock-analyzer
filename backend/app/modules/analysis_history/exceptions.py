from app.core.exceptions import AppError


class AnalysisNotReadyError(AppError):
    def __init__(self, message: str = "Analysis not ready") -> None:
        super().__init__(message, "ANALYSIS_NOT_READY")
