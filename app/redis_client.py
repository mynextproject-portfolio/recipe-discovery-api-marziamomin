import redis
import json
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for caching MealDB search results."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis client.
        
        Args:
            redis_url: Redis connection URL
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _make_cache_key(self, search_query: str) -> str:
        """Generate cache key for search query.
        
        Args:
            search_query: The search query string
            
        Returns:
            Cache key string
        """
        # Normalize query for consistent cache keys
        normalized_query = search_query.strip().lower()
        return f"mealdb_search:{normalized_query}"
    
    def get_cached_results(self, search_query: str) -> Optional[list]:
        """Get cached search results from Redis.
        
        Args:
            search_query: The search query string
            
        Returns:
            Cached results as list, or None if not found
        """
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._make_cache_key(search_query)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                results = json.loads(cached_data)
                logger.info(f"Cache hit for query: '{search_query}'")
                return results
            else:
                logger.info(f"Cache miss for query: '{search_query}'")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def cache_results(self, search_query: str, results: list, ttl_seconds: int = 86400) -> bool:
        """Cache search results in Redis.
        
        Args:
            search_query: The search query string
            results: List of search results to cache
            ttl_seconds: Time to live in seconds (default: 24 hours)
            
        Returns:
            True if caching succeeded, False otherwise
        """
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._make_cache_key(search_query)
            json_data = json.dumps(results)
            
            self.redis_client.setex(cache_key, ttl_seconds, json_data)
            logger.info(f"Cached {len(results)} results for query: '{search_query}' (TTL: {ttl_seconds}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching results: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Redis is available.
        
        Returns:
            True if Redis is available, False otherwise
        """
        if not self.redis_client:
            return False
            
        try:
            self.redis_client.ping()
            return True
        except:
            return False
