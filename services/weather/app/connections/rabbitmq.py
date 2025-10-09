from aio_pika import connect_robust, RobustConnection, RobustChannel
from typing import Optional

from app.core.config import settings

class RabbitMQ:
    def __init__(self, url: str = settings.RABBIT_URL):
        self.url = url
        self.connection: Optional[RobustConnection] = None
        self.channel: Optional[RobustChannel] = None

    async def connect(self):
        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()

    async def close(self):
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

rabbitmq = RabbitMQ()