from datetime import datetime, date
import json
import math
import aiohttp
import logging
import aio_pika

from app.connections.redis import redis_client
from app.connections.rabbitmq import RabbitMQ
from app.schemas.weather import *
from app.schemas.forecast import *
from app.core.config import settings
from app.core.logger import logger

class ForecastRepository:

    def __init__(self, rabbitmq: RabbitMQ):
        self.rabbitmq = rabbitmq

    async def get_forecast_from_redis(self, task_id) -> ForecastData:
        '''Получает прогноз из Redis'''
        data = redis_client.client.get(f'forecast:{task_id}')
        if not data:
            return None
        return ForecastData.model_validate_json(data)
    
    async def request_forecast_calculation(self, task_id, city, date):
        msg = MQForecastRequest(
            task_id=task_id,
            city=city,
            date_=date
        )
        
        channel = self.rabbitmq.channel
        queue = await channel.declare_queue('forecast_requests', durable=True)

        message_body = msg.model_dump_json().encode()
        message = aio_pika.Message(body=message_body)
        await channel.default_exchange.publish(
            message,
            routing_key=queue.name  # или settings.RABBITMQ_FC_REQ_QUEUE
        )
        logger.info(f'Forecast request sent to task queue: {city} {date}')