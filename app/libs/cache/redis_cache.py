import json
from typing import Iterable

from app.libs import cache


class RedisCache:
    """
    RedisCache class provides an interface to interact with a Redis cache for storing and retrieving objects.
    
    Methods:
        mget(cache_keys: list[str]) -> Optional[float]:
            Retrieves the key values from the Redis cache.
            Args:
                cache_key (list[str]): The keys to retrieve from cache.
            Returns:
                Any: The value from cache, or None if not found.
        
        mset(key: str, value: list[any]) -> bool:
            Sets the values of a key in the Redis cache.
            Args:
                data (dict): The data to be set in redis
            Returns:
                bool: True if successful, False otherwise.
    """

    def mget(self, keys: Iterable[str]) -> list:
        """
        Get the value of the given keys which exists.
        :param keys: keys which needs to be retrieved.
        """
        values = cache.REDIS_CLIENT.mget(*keys)
        return [json.loads(value) if value else value for value in values]

    def mset(self, data: dict) -> bool:
        """
        set the value of the given keys in bulk.
        :param data: key value pair data to be set.
        """
        return cache.REDIS_CLIENT.mset(data)


# Create a singleton instance for use across the application
cache_client = RedisCache()
