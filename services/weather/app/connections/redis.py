import redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            # password=settings.REDIS_PASSWORD,
            decode_responses=True  # Автоматически декодирует bytes в str
        )

    async def ping(self):
        return self.client.ping()

redis_client = RedisClient()