import asyncio
import aio_pika
import json
import time
from pydantic import BaseModel, Field
import redis
import uuid
from typing import Literal
from datetime import date, datetime
from predictor import ForecasterLinear
from settings import settings

class MQForecastRequest(BaseModel):
    task_id: uuid.UUID
    city: str
    date_: date

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

async def process_message(message: aio_pika.IncomingMessage, redis_client: redis.Redis):
    """Обработка полученного сообщения."""
    async with message.process():
        data = json.loads(message.body)
        request = MQForecastRequest(**data)

        forecaster = ForecasterLinear()
        await forecaster.fit(request.city, request.date_)
        time.sleep(3)
        forecast = forecaster.predict(request.date_)

        fc = ForecastData(
            metadata=ForecastMetadata(
                model='linear_regression',
                predicted_at=datetime.now()
            ),
            forecast=Forecast(
                temp_min=forecast['temp_min'],
                temp_mean=forecast['temp_avg'],
                temp_max=forecast['temp_max']
            )
        )
        
        # Сохраняем результат в Redis
        redis_client.set(f'forecast:{request.task_id}', fc.model_dump_json())
        print(f'Stored forecast for {request.task_id}: {request.city} on {request.date_}')

async def main():
    # Устанавливаем соединение с RabbitMQ
    rabbit_connection = await aio_pika.connect_robust(
        settings.RABBIT_URL
    )

    async with rabbit_connection:
        channel = await rabbit_connection.channel()
        
        # Создаем клиент Redis
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT
        )

        # Объявляем очередь
        queue = await channel.declare_queue(
            settings.RABBITMQ_FC_REQ_QUEUE,
            durable=True
        )

        print("Waiting for messages...")
        
        # Начинаем потребление сообщений
        await queue.consume(lambda msg: process_message(msg, redis_client))

        await asyncio.Future()  # Бесконечное ожидание

asyncio.run(main())
