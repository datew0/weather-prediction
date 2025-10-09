from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List
from app.core.config import settings

class WeatherQuery(BaseModel):
    '''Параметры запроса погоды в конкретном городе на определенную дату'''
    city: str = Field(..., description='Город', example="Moscow")
    date_: date = Field(..., alias='date', lt=date.today())

    @field_validator('city')
    def validate_city(cls, value):
        allowed_cities = settings.ALLOWED_CITIES_COORDS.keys()
        if value not in allowed_cities:
            raise ValueError(f'City must be one of: {", ".join(allowed_cities)}')
        return value


class WeatherData(BaseModel):
    '''Данные о погоде за день'''
    temp_min: float                     # Минимальная температура
    temp_avg: float                     # Средняя температура
    temp_max: float                     # Максимальная температура
    
    humidity_min: float # Минимальная влажность (опционально)
    humidity_avg: float                 # Средняя влажность
    humidity_max: float # Максимальная влажность (опционально)

    precipitation: float                # Осадки (мм)


class WeatherResponse(WeatherQuery):
    '''Ответ на запрос погоды'''
    weather: WeatherData


class OpenMeteoReqParams(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Широта от -90 до 90")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота от -180 до 180")
    start_date: date = Field(..., description="Начальная дата в формате YYYY-MM-DD")
    end_date: date = Field(..., description="Конечная дата в формате YYYY-MM-DD")
    daily: List[str] = Field(
        default=["temperature_2m_mean"],
        description="Список ежедневных параметров для получения"
    )
    timezone: Optional[str] = Field(
        default="auto",
        description="Часовой пояс (например, 'Europe/Moscow')"
    )

    def to_api_params(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "daily": ",".join(self.daily),
            "timezone": self.timezone
        }

class OpenMeteoDailyData(BaseModel):
    time: List[date]
    temperature_2m_mean: List[Optional[float]]
    temperature_2m_min: List[Optional[float]]
    temperature_2m_max: List[Optional[float]]
    relative_humidity_2m_mean: List[Optional[float]]
    relative_humidity_2m_min: List[Optional[float]]
    relative_humidity_2m_max: List[Optional[float]]
    precipitation_sum: List[Optional[float]]

class OpenMeteoResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    daily_units: dict
    daily: OpenMeteoDailyData