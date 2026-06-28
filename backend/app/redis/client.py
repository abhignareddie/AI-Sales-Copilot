import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger

redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True,
        )
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")


async def invalidate_recommendation_cache():
    """Delete all cached Gemini elements from Redis cache."""
    global redis_client
    if redis_client is None:
        await get_redis()
    if redis_client:
        try:
            keys = await redis_client.keys("gemini:*")
            if keys:
                await redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} recommendation cache keys.")
        except Exception as e:
            logger.warning(f"Failed to invalidate cache: {e}")

