from datetime import datetime, date
import json
import math
import aiohttp

from app.connections.redis import redis_client
from app.schemas.weather import *
from app.core.config import settings
from app.core.logger import logger

class WeatherRepository:
    @staticmethod
    def _generate_key(city, date: date) -> str:
        return f"weather:{city}:{date.isoformat()}"
    
    @staticmethod
    def _convert_openmeteo_to_weather(data: OpenMeteoResponse) -> WeatherData:
        return WeatherData(
            temp_min = data.daily.temperature_2m_min[0],
            temp_avg = data.daily.temperature_2m_mean[0],
            temp_max = data.daily.temperature_2m_max[0],
            humidity_min = data.daily.relative_humidity_2m_min[0],
            humidity_avg = data.daily.relative_humidity_2m_mean[0],
            humidity_max = data.daily.relative_humidity_2m_max[0],
            precipitation=data.daily.precipitation_sum[0]
        )

    async def save_weather_to_redis(self, city, date: date, weather: WeatherData) -> None:
        """Сохраняет данные погоды в Redis."""
        key = self._generate_key(city, date)
        
        redis_client.client.set(
            name=key,
            value=weather.model_dump_json(),
            ex=60 * 60 * 24 # 1 day
        )

    async def get_weather_from_redis(self, city, date: date) -> WeatherData | None:
        """Получает данные погоды из Redis."""
        key = self._generate_key(city, date)
        data = redis_client.client.get(key)
        if not data:
            return None
        logger.info('Fetching weather data from Redis')
        return WeatherData.model_validate_json(data)  # Десериализуем JSON в Pydantic-модель

    async def get_weather_from_api(self, city, date_: date) -> WeatherData | None:
        logger.info(f'Requesting weather in {city} on {date_.isoformat()} from API')
        lat = settings.ALLOWED_CITIES_COORDS[city][0]
        lon = settings.ALLOWED_CITIES_COORDS[city][1]
        async with aiohttp.ClientSession() as session:
            params = OpenMeteoReqParams(
                latitude = lat,
                longitude = lon,
                start_date = date_,
                end_date = date_,
                daily = [
                    "temperature_2m_mean",
                    "temperature_2m_min",
                    "temperature_2m_max",
                    "precipitation_sum",
                    "relative_humidity_2m_mean",
                    "relative_humidity_2m_max",
                    "relative_humidity_2m_min"
                ]
            )

            async with session.get(url = settings.ARCHIVE_WEATHER_URL, params = params.to_api_params()) as response:
                if response.status == 200:
                    data = await response.json()
                    weather_response = OpenMeteoResponse(**data)
                    return self._convert_openmeteo_to_weather(weather_response)
                else:
                    return None
