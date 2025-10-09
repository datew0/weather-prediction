from datetime import datetime, date
import hashlib
import asyncio
import uuid

from app.connections.redis import redis_client
from app.core.config import settings
from app.core.logger import logger
from app.repositories.forecast import ForecastRepository
from app.schemas.forecast import ForecastData

class ForecastService:
    def __init__(self, repo: ForecastRepository):
        self.repo = repo

    @staticmethod
    def _generate_task_id(city: str, date_: date) -> uuid.UUID:
        input_str = f"{city}:{date_.isoformat()}"
        hash_obj = hashlib.sha256(input_str.encode('utf-8'))
        uuid_bytes = hash_obj.digest()[:16]
        return uuid.UUID(bytes=uuid_bytes)

    async def get_forecast(self, task_id) -> ForecastData:
        '''Получение прогноза'''
        if (fc := await self.repo.get_forecast_from_redis(task_id)) is not None:
            return fc
        return None
        
    async def request_forecast(self, city, date: date) -> uuid.UUID:
        '''Запрос нового прогноза'''
        task_id = self._generate_task_id(city, date)

        fc = await self.repo.get_forecast_from_redis(task_id)
        if fc is None:
            # Закинуть сообщение
            asyncio.create_task(self.repo.request_forecast_calculation(task_id, city, date))
            return task_id
        logger.info(f'Forecast already available: {city} {date}')
        return None