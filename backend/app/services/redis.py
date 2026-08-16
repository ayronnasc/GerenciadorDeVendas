import redis

from app.settings import Settings

settings = Settings()

redis_client = redis.Redis(
    host=getattr(settings, "REDIS_HOST", "localhost"),
    port=getattr(settings, "REDIS_PORT", 6379),
    decode_responses=True
)