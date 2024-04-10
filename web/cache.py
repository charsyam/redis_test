class CacheDefinition:
    def __init__(self, prefix, ttl_seconds, description):
        self._prefix = prefix
        self._ttl_seconds = ttl_seconds
        self._description = description


class Cache:
    TKEY = CacheDefinition("tkey", 300, "key 설명")

    def __init__(self, conn):
        self._conn = conn

    def key(self, definition, key):
        return f"{definition._prefix}:{key}"

    def set(self, definition, key, value):
        cache_key = self.key(definition, key)
        return self._conn.set(cache_key, value)

    def get(self, definition, key):
        cache_key = self.key(definition, key)
        return self._conn.get(cache_key)
