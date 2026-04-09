from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging, get_logger
from app.db import models  # noqa: F401
from app.db.seed import run_all_seeds
from app.db.session import SessionLocal, init_db_schema
from app.shared.schemas.common import ApiErrorBody, ApiSuccessResponse, HealthData

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        init_db_schema()
        with SessionLocal() as session:
            run_all_seeds(session)
    except Exception:
        logger.exception(
            "Không khởi tạo DB/seed (kiểm tra MySQL và DATABASE_URL). API cần DB sẽ lỗi."
        )
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    body = ApiErrorBody(message=exc.message, error_code=exc.error_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(by_alias=True),
    )


@app.exception_handler(RequestValidationError)
def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    body = ApiErrorBody(
        message="Validation error",
        error_code="VALIDATION_ERROR",
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=body.model_dump(by_alias=True),
    )


@app.get("/health")
def health() -> ApiSuccessResponse[HealthData]:
    return ApiSuccessResponse(data=HealthData())


app.include_router(api_router, prefix=settings.api_v1_prefix)
