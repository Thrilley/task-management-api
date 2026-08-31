import json
import logging
from typing import Any

from redis import RedisError
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_task_list(cache_key: str) -> list[dict[str, Any]] | None:
    try:
        raw_value = await redis_client.get(cache_key)
        return json.loads(raw_value) if raw_value else None
    except RedisError:
        logger.warning("Redis is unavailable; reading task list from PostgreSQL")
        return None


async def set_task_list(cache_key: str, value: list[dict[str, Any]]) -> None:
    try:
        await redis_client.set(cache_key, json.dumps(value), ex=60)
    except RedisError:
        logger.warning("Redis is unavailable; skipping task-list cache write")


async def invalidate_task_list_cache() -> None:
    try:
        keys = [key async for key in redis_client.scan_iter(match="tasks:list:*")]
        if keys:
            await redis_client.delete(*keys)
    except RedisError:
        logger.warning("Redis is unavailable; skipping task-list cache invalidation")


async def close_cache_connection() -> None:
    await redis_client.aclose()
