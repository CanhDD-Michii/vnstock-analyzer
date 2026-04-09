from fastapi import APIRouter

from app.api.v1 import admin, analysis, auth, stocks

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(stocks.router)
api_router.include_router(analysis.router)
api_router.include_router(admin.router)
