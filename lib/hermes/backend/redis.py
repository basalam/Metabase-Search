import time

import redis

from . import AbstractBackend, AbstractLock

__all__ = "Lock", "Backend"


class Lock(AbstractLock):
    """
    Key-aware distributed lock. "Distributed" is in sense of clients,
    not Redis instances. Implemented as described in *Correct
    implementation with a single instance* [1]_, but without setting
    unique value to the lock entry and later checking it, because it
    is expected for a cached function to complete before lock timeout.

    .. [1] http://redis.io/topics/distlock#correct-implementation-with-a-single-instance
    """

    client = None
    """Redis client."""

    timeout = 900
    """Maximum TTL of lock."""

    sleep = 0.1
    """Amount of time to sleep per ``while True`` iteration when waiting."""

    def __init__(self, key, client, *, sleep=None, timeout=None):
        super().__init__(key)

        self.client = client

        self.sleep = sleep if sleep is not None else self.sleep
        self.timeout = timeout if timeout is not None else self.timeout

    def acquire(self, wait=True):
        while True:
            if self.client.set(self.key, "locked", nx=True, ex=self.timeout):
                return True
            elif not wait:
                return False
            else:
                time.sleep(self.sleep)

    def release(self):
        self.client.delete(self.key)


class Backend(AbstractBackend):
    """Redis backend implementation."""

    client = None
    """Redis client."""

    _lockSleep = None
    _lockTimeout = None

    def __init__(
        self,
        mangler,
        *,
        host="localhost",
        password=None,
        port=6379,
        db=0,
        lockSleep=None,
        lockTimeout=None,
        **kwargs
    ):
        super().__init__(mangler)

        # Redis client creates a pool that connects lazily
        self.client = redis.StrictRedis(host, port, db, password, **kwargs)

        self._lockSleep = lockSleep
        self._lockTimeout = lockTimeout

    def lock(self, key):
        return Lock(
            self.mangler.nameLock(key),
            self.client,
            sleep=self._lockSleep,
            timeout=self._lockTimeout,
        )

    def save(self, key=None, value=None, *, mapping=None, ttl=None):
        if not mapping:
            mapping = {key: value}
        mapping = {k: self.mangler.dumps(v) for k, v in mapping.items()}

        if not ttl:
            self.client.mset(mapping)
        else:
            pipeline = self.client.pipeline()
            for k, v in mapping.items():
                pipeline.setex(k, ttl, v)
            pipeline.execute()

    def load(self, keys):
        if self._isScalar(keys):
            value = self.client.get(keys)
            if value is not None:
                value = self.mangler.loads(value)
            return value
        else:
            keys = tuple(keys)
            return {
                k: self.mangler.loads(v)
                for k, v in zip(keys, self.client.mget(keys))
                if v is not None
            }

    def remove(self, keys):
        if self._isScalar(keys):
            keys = (keys,)

        self.client.delete(*keys)

    def clean(self):
        self.client.flushdb()
