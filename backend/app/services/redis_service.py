"""
Financial Intelligence Platform - Redis Service

Redis connection management and caching operations.
"""

import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisManager:
    """
    Redis connection and cache manager.
    
    Provides methods for:
    - Connection management
    - String operations
    - Hash operations
    - List operations
    - Pub/Sub
    - Data serialization
    """
    
    def __init__(self):
        self.client: Optional[Redis] = None
        self.pool: Optional[ConnectionPool] = None
    
    async def connect(self) -> None:
        """
        Establish connection to Redis.
        """
        try:
            logger.info("Connecting to Redis...")
            
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                max_connections=50,
                decode_responses=True
            )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close Redis connection.
        """
        try:
            if self.client:
                await self.client.close()
                logger.info("Redis connection closed")
            
            if self.pool:
                await self.pool.disconnect()
                
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    async def ping(self) -> bool:
        """
        Check if Redis is responsive.
        
        Returns:
            True if Redis is available
        """
        try:
            response = await self.client.ping()
            return response
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            raise
    
    # =========================================================================
    # String Operations
    # =========================================================================
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key.
        
        Args:
            key: Redis key
        
        Returns:
            Value or None if key doesn't exist
        """
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            raise
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value by key.
        
        Args:
            key: Redis key
            value: Value to store
            expire: Expiration time in seconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
        
        Returns:
            True if value was set
        """
        try:
            # Serialize value if needed
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            return await self.client.set(key, value, ex=expire, nx=nx, xx=xx)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            raise
    
    async def setex(self, key: str, seconds: int, value: Any) -> bool:
        """
        Set value with expiration.
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
            value: Value to store
        
        Returns:
            True if value was set
        """
        return await self.set(key, value, expire=seconds)
    
    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.
        
        Args:
            keys: Keys to delete
        
        Returns:
            Number of keys deleted
        """
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete error for keys {keys}: {e}")
            raise
    
    async def exists(self, *keys: str) -> int:
        """
        Check if keys exist.
        
        Args:
            keys: Keys to check
        
        Returns:
            Number of keys that exist
        """
        try:
            return await self.client.exists(*keys)
        except Exception as e:
            logger.error(f"Redis exists error for keys {keys}: {e}")
            raise
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set key expiration.
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
        
        Returns:
            True if expiration was set
        """
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire error for key {key}: {e}")
            raise
    
    async def ttl(self, key: str) -> int:
        """
        Get key TTL (time to live).
        
        Args:
            key: Redis key
        
        Returns:
            TTL in seconds (-1 if no expiry, -2 if key doesn't exist)
        """
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis ttl error for key {key}: {e}")
            raise
    
    # =========================================================================
    # Hash Operations
    # =========================================================================
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """
        Get value from hash.
        
        Args:
            name: Hash name
            key: Field name
        
        Returns:
            Field value or None
        """
        try:
            return await self.client.hget(name, key)
        except Exception as e:
            logger.error(f"Redis hget error for hash {name}: {e}")
            raise
    
    async def hset(
        self,
        name: str,
        key: str,
        value: Any,
        mapping: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Set value in hash.
        
        Args:
            name: Hash name
            key: Field name
            value: Field value
            mapping: Optional dict of field-value pairs
        
        Returns:
            Number of fields added
        """
        try:
            if mapping:
                # Serialize nested values
                serialized = {}
                for k, v in mapping.items():
                    if isinstance(v, (dict, list)):
                        serialized[k] = json.dumps(v)
                    else:
                        serialized[k] = v
                return await self.client.hset(name, mapping=serialized)
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            return await self.client.hset(name, key, value)
        except Exception as e:
            logger.error(f"Redis hset error for hash {name}: {e}")
            raise
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """
        Get all fields from hash.
        
        Args:
            name: Hash name
        
        Returns:
            Dict of field-value pairs
        """
        try:
            return await self.client.hgetall(name)
        except Exception as e:
            logger.error(f"Redis hgetall error for hash {name}: {e}")
            raise
    
    async def hdel(self, name: str, *keys: str) -> int:
        """
        Delete fields from hash.
        
        Args:
            name: Hash name
            keys: Field names to delete
        
        Returns:
            Number of fields deleted
        """
        try:
            return await self.client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis hdel error for hash {name}: {e}")
            raise
    
    # =========================================================================
    # List Operations
    # =========================================================================
    
    async def lpush(self, name: str, *values: Any) -> int:
        """
        Push values to list head.
        
        Args:
            name: List name
            values: Values to push
        
        Returns:
            List length after push
        """
        try:
            serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
            return await self.client.lpush(name, *serialized)
        except Exception as e:
            logger.error(f"Redis lpush error for list {name}: {e}")
            raise
    
    async def rpush(self, name: str, *values: Any) -> int:
        """
        Push values to list tail.
        
        Args:
            name: List name
            values: Values to push
        
        Returns:
            List length after push
        """
        try:
            serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
            return await self.client.rpush(name, *serialized)
        except Exception as e:
            logger.error(f"Redis rpush error for list {name}: {e}")
            raise
    
    async def lrange(self, name: str, start: int, end: int) -> List[str]:
        """
        Get range of values from list.
        
        Args:
            name: List name
            start: Start index
            end: End index (-1 for all)
        
        Returns:
            List of values
        """
        try:
            return await self.client.lrange(name, start, end)
        except Exception as e:
            logger.error(f"Redis lrange error for list {name}: {e}")
            raise
    
    async def ltrim(self, name: str, start: int, end: int) -> bool:
        """
        Trim list to specified range.
        
        Args:
            name: List name
            start: Start index
            end: End index
        
        Returns:
            True if successful
        """
        try:
            return await self.client.ltrim(name, start, end)
        except Exception as e:
            logger.error(f"Redis ltrim error for list {name}: {e}")
            raise
    
    async def llen(self, name: str) -> int:
        """
        Get list length.
        
        Args:
            name: List name
        
        Returns:
            List length
        """
        try:
            return await self.client.llen(name)
        except Exception as e:
            logger.error(f"Redis llen error for list {name}: {e}")
            raise
    
    # =========================================================================
    # Set Operations
    # =========================================================================
    
    async def sadd(self, name: str, *values: Any) -> int:
        """
        Add values to set.
        
        Args:
            name: Set name
            values: Values to add
        
        Returns:
            Number of elements added
        """
        try:
            return await self.client.sadd(name, *values)
        except Exception as e:
            logger.error(f"Redis sadd error for set {name}: {e}")
            raise
    
    async def smembers(self, name: str) -> set:
        """
        Get all set members.
        
        Args:
            name: Set name
        
        Returns:
            Set of members
        """
        try:
            return await self.client.smembers(name)
        except Exception as e:
            logger.error(f"Redis smembers error for set {name}: {e}")
            raise
    
    async def sismember(self, name: str, value: Any) -> bool:
        """
        Check if value is in set.
        
        Args:
            name: Set name
            value: Value to check
        
        Returns:
            True if value is member
        """
        try:
            return await self.client.sismember(name, value)
        except Exception as e:
            logger.error(f"Redis sismember error for set {name}: {e}")
            raise
    
    # =========================================================================
    # Sorted Set Operations
    # =========================================================================
    
    async def zadd(
        self,
        name: str,
        mapping: Dict[str, float],
        nx: bool = False,
        xx: bool = False
    ) -> int:
        """
        Add members to sorted set.
        
        Args:
            name: Sorted set name
            mapping: Dict of member -> score
            nx: Only add new members
            xx: Only update existing members
        
        Returns:
            Number of members added
        """
        try:
            return await self.client.zadd(name, mapping, nx=nx, xx=xx)
        except Exception as e:
            logger.error(f"Redis zadd error for sorted set {name}: {e}")
            raise
    
    async def zrangebyscore(
        self,
        name: str,
        min: Union[float, str],
        max: Union[float, str],
        withscores: bool = False
    ) -> List[Any]:
        """
        Get members by score range.
        
        Args:
            name: Sorted set name
            min: Minimum score
            max: Maximum score
            withscores: Include scores in return
        
        Returns:
            List of members (and scores if requested)
        """
        try:
            return await self.client.zrangebyscore(
                name, min, max, withscores=withscores
            )
        except Exception as e:
            logger.error(f"Redis zrangebyscore error for sorted set {name}: {e}")
            raise
    
    async def zremrangebyrank(
        self,
        name: str,
        start: int,
        end: int
    ) -> int:
        """
        Remove members by rank range.
        
        Args:
            name: Sorted set name
            start: Start rank
            end: End rank
        
        Returns:
            Number of members removed
        """
        try:
            return await self.client.zremrangebyrank(name, start, end)
        except Exception as e:
            logger.error(f"Redis zremrangebyrank error for sorted set {name}: {e}")
            raise
    
    # =========================================================================
    # Pub/Sub Operations
    # =========================================================================
    
    async def publish(self, channel: str, message: Any) -> int:
        """
        Publish message to channel.
        
        Args:
            channel: Channel name
            message: Message to publish
        
        Returns:
            Number of subscribers that received message
        """
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            
            return await self.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis publish error for channel {channel}: {e}")
            raise
    
    def pubsub(self):
        """
        Get pub/sub subscriber.
        
        Returns:
            Pub/Sub instance
        """
        return self.client.pubsub()
    
    # =========================================================================
    # Pipeline Operations
    # =========================================================================
    
    def pipeline(self):
        """
        Get pipeline for batch operations.
        
        Returns:
            Pipeline instance
        """
        return self.client.pipeline()
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    async def flush_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "quote:*")
        
        Returns:
            Number of keys deleted
        """
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis flush_pattern error for pattern {pattern}: {e}")
            raise
    
    async def get_or_set(
        self,
        key: str,
        callback,
        expire: Optional[int] = None
    ) -> Any:
        """
        Get value or set with callback if not exists.
        
        Args:
            key: Redis key
            callback: Async function to get/set value
            expire: Optional expiration
        
        Returns:
            Cached or computed value
        """
        value = await self.get(key)
        
        if value is not None:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        
        # Cache miss - compute value
        value = await callback()
        
        # Cache the result
        await self.set(key, value, expire=expire)
        
        return value
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment value by amount.
        
        Args:
            key: Redis key
            amount: Increment amount
        
        Returns:
            New value
        """
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis increment error for key {key}: {e}")
            raise
    
    async def set_nx(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Set value only if key doesn't exist.
        
        Args:
            key: Redis key
            value: Value to store
            expire: Optional expiration
        
        Returns:
            True if value was set (key didn't exist)
        """
        return await self.set(key, value, expire=expire, nx=True)


# Global Redis manager instance
redis_manager = RedisManager()

