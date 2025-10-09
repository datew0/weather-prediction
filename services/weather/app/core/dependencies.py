from fastapi import Depends, Request

from app.services.weather import WeatherService
from app.repositories.weather import WeatherRepository
from app.services.forecast import ForecastService
from app.repositories.forecast import ForecastRepository

def get_weather_service() -> WeatherService:
    repo = WeatherRepository()
    return WeatherService(repo)

def get_rabbitmq(request: Request):
    return request.app.state.rabbitmq

def get_forecast_service(rabbitmq = Depends(get_rabbitmq)) -> ForecastService:
    repo = ForecastRepository(rabbitmq)
    return ForecastService(repo)
