from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import date, datetime, timedelta
import uuid

from app.utils.cities import ALLOWED_CITIES_COORDS

class ForecastPostRequest(BaseModel):
    '''Параметры запроса прогноза по городу и дате'''
    city: str = Field(..., example='Moscow')
    date_: date = Field(..., alias='date', validation_alias='date_')

    @field_validator('city')
    def validate_city(cls, value: str) -> str:
        allowed_cities = ALLOWED_CITIES_COORDS.keys()
        if value not in allowed_cities:
            raise ValueError(f'Неподдерживаемый город: {", ".join(allowed_cities)}')
        return value

    @field_validator('date_')
    def validate_date(cls, value: date) -> date:
        week_later = date.today() + timedelta(weeks=1)
        if value < week_later:
            return value
        raise ValueError(f'Дата прогноза не может быть позже {week_later}')
    
class ForecastTaskQuery(BaseModel):
    task_id: uuid.UUID

class ForecastPostResponse(BaseModel):
    status: Literal['accepted', 'rejected']
    task_id: uuid.UUID
    msg: str

class ForecastMetadata(BaseModel):
    model: Literal['linear_regression'] = Field(..., description="Использованная модель прогнозирования")
    predicted_at: datetime = Field(..., description="Время создания прогноза")
    
class Forecast(BaseModel):
    temp_min: float
    temp_mean: float
    temp_max: float

class ForecastData(BaseModel):
    metadata: ForecastMetadata
    forecast: Forecast

class ForecastResponse(ForecastData):
    pass

class MQForecastRequest(BaseModel):
    task_id: uuid.UUID
    city: str
    date_: date