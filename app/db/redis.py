"""
Redis configuration and connection management
"""
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from typing import Optional

from app.core.config import settings


class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        self.pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            retry_on_timeout=True,
        )
        self.client = redis.Redis(connection_pool=self.pool)
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
    
    async def get_client(self) -> redis.Redis:
        """Get Redis client"""
        if not self.client:
            await self.connect()
        return self.client


# Global Redis client instance
redis_client = RedisClient()


async def get_redis():
    """
    Dependency to get Redis client
    """
    return await redis_client.get_client()


# Redis utility functions
async def set_cache(key: str, value: str, expire: int = 3600):
    """Set cache with expiration"""
    client = await get_redis()
    await client.setex(key, expire, value)


async def get_cache(key: str) -> Optional[str]:
    """Get cache value"""
    client = await get_redis()
    return await client.get(key)


async def delete_cache(key: str):
    """Delete cache"""
    client = await get_redis()
    await client.delete(key)


async def add_to_set(key: str, value: str):
    """Add value to set"""
    client = await get_redis()
    await client.sadd(key, value)


async def remove_from_set(key: str, value: str):
    """Remove value from set"""
    client = await get_redis()
    await client.srem(key, value)


async def is_in_set(key: str, value: str) -> bool:
    """Check if value is in set"""
    client = await get_redis()
    return await client.sismember(key, value)

