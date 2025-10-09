import asyncio
import aio_pika
import aiohttp
import json
import time
from pydantic import BaseModel, Field
import redis
import uuid
from typing import Literal
from datetime import date, datetime
from predictor import ForecasterCatBoost

class MQForecastRequest(BaseModel):
    task_id: uuid.UUID
    city: str
    date_: date

class ForecastMetadata(BaseModel):
    model: Literal['catboost-1.0'] = Field(..., description="Использованная модель прогнозирования")
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

        forecaster = ForecasterCatBoost()
        await forecaster.fit(request.city, request.date_)
        time.sleep(3)
        forecast = forecaster.predict(request.date_)

        fc = ForecastData(
            metadata=ForecastMetadata(
                model='catboost-1.0',
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
    rabbit_connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    async with rabbit_connection:
        channel = await rabbit_connection.channel()
        
        # Создаем клиент Redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0)

        # Объявляем очередь
        queue = await channel.declare_queue('forecast_requests', durable=True)

        # Начинаем потребление сообщений
        await queue.consume(lambda msg: process_message(msg, redis_client))

        print("Waiting for messages...")
        await asyncio.Future()  # Бесконечное ожидание

# Запускаем консюмера
if __name__ == '__main__':
    asyncio.run(main())
