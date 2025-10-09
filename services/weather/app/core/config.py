from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator
)
from typing import Annotated, Any, Literal, Dict, Tuple

from pydantic_settings import BaseSettings, EnvSettingsSource

class Settings(BaseSettings):
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    ARCHIVE_WEATHER_URL: str = "https://archive-api.open-meteo.com/v1/archive"
    ALLOWED_CITIES_COORDS: Dict[str, Tuple[float, float]] = {
        'Moscow': (55.7558, 37.6173),        # Исправлено на правильные координаты
        'New-York': (40.7128, -74.0060),     # Исправлено на правильные координаты
        'Washington': (38.9072, -77.0369),   # Координаты верные
        'London': (51.5074, -0.1278),        # Лондон
        'Tokyo': (35.6762, 139.6503),        # Токио
        'Paris': (48.8566, 2.3522),          # Париж
        'Sydney': (33.8688, 151.2093),       # Сидней
        'Berlin': (52.5200, 13.4050),        # Берлин
        'Rio-de-Janeiro': (22.9068, -43.1729), # Рио-де-Жанейро
        'Cape-Town': (33.9249, 18.4241),     # Кейптаун
        'Delhi': (28.6139, 77.2090)          # Дели
    }

    PROJECT_NAME: str = "Weather Service"

    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379

    RABBITMQ_HOST: str = 'rmq'
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = 'guest'
    RABBITMQ_PASS: str = 'guest'
    RABBITMQ_FC_REQ_QUEUE: str = 'forecast_requests'
    RABBIT_URL: str = f'amqp://{RABBITMQ_USER}:' \
             f'{RABBITMQ_PASS}@' \
             f'{RABBITMQ_HOST}:' \
             f'{RABBITMQ_PORT}/'
    
    class Config:
        env_source = EnvSettingsSource

settings = Settings()