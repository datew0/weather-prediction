from datetime import date
import asyncio

from app.repositories.weather import WeatherRepository
from app.schemas.weather import WeatherData

class WeatherService:
    def __init__(self, repo: WeatherRepository):
        self.repo = repo

    async def get_weather(self, city, date: date) -> WeatherData:
        '''Запрос погоды из Redis-кеша. В случае отсутствия обращение к API'''
        # Пробуем получить из кеша
        if (w := await self.repo.get_weather_from_redis(city, date)) is not None:
            return w
        
        # Если нет в кеше - запрашиваем API
        if (w := await self.repo.get_weather_from_api(city, date)) is not None:
            # Сохраняем в кеш (не дожидаемся завершения)
            asyncio.create_task(self.repo.save_weather_to_redis(city, date, w))
            return w
        
        return None
    
    async def request_forecast(self, city, date: date):
        self.repo.put_forecast_request
