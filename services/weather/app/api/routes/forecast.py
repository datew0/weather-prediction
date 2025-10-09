from fastapi import APIRouter, Depends, HTTPException, Query, status
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from pydantic import ValidationError
from typing import Annotated

from app.schemas.forecast import *
from app.services.forecast import ForecastService
from app.core.dependencies import get_forecast_service

router = APIRouter(tags=["forecast"])

@router.get("/forecast")
async def get_forecast_results(query: Annotated[ForecastTaskQuery, Query()], 
                               service: ForecastService = Depends(get_forecast_service)):
    
    fc = await service.get_forecast(query.task_id)

    if not fc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Прогноз с идентификатором {query.task_id} не найден'
        )

    response = fc
    return response

@router.post("/forecast",
             status_code=status.HTTP_202_ACCEPTED,
             response_model=ForecastPostResponse)
async def request_forecast(req: ForecastPostRequest,
                           service: ForecastService = Depends(get_forecast_service)):
    
    task_id = await service.request_forecast(req.city, req.date_)

    if task_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Forecast already exists for specified parameters"
        )

    response = ForecastPostResponse(
        status='accepted',
        task_id=task_id,
        msg="Ваш запрос на формирование прогноза передан в обработку"
    )

    return response

