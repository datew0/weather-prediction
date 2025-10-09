from fastapi import APIRouter, Depends

from app.services.weather import WeatherService
from app.schemas.weather import WeatherQuery, WeatherResponse
from app.core.dependencies import get_weather_service

router = APIRouter(tags=["weather"])

@router.get("/weather",
            summary='Получить погоду',
            response_model=WeatherResponse)
async def get_weather(query: WeatherQuery = Depends(),
                      service: WeatherService = Depends(get_weather_service)):
    '''
    Возвращает метеорологические данные для заданного города на указанную дату
    - **city**: название города
    - **date**: дата
    '''
    weather = await service.get_weather(
        query.city,
        date=query.date_
    )
    
    response = WeatherResponse(
        city=query.city,
        date=query.date_,
        weather=weather
    )

    return response
