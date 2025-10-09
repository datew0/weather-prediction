from fastapi import APIRouter

from app.api.routes import weather, forecast

api_router = APIRouter()
api_router.include_router(weather.router)
api_router.include_router(forecast.router)