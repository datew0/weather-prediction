from typing import Dict, Tuple, Literal
from pydantic_settings import BaseSettings
from pathlib import Path

# Путь к .env файлу на уровень выше app/
BASE_DIR = Path(__file__).resolve()
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    WEATHER_HOST: str
    WEATHER_PORT: int

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_FC_REQ_QUEUE: str

    @property
    def RABBIT_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    class Config:
        # Если .env существует — используем его, иначе читаем из окружения
        env_file = ENV_PATH if ENV_PATH.exists() else None
        env_file_encoding = "utf-8"

settings = Settings()
