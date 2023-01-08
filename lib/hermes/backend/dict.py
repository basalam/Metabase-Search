import time
import heapq
import threading

from . import AbstractBackend, AbstractLock

__all__ = 'Lock', 'Backend'


class Lock(AbstractLock):
    '''Key-unaware thread lock.'''

    _lock = None
    '''Threading lock instance.'''

    def __init__(self, key):
        self._lock = threading.RLock()

    def acquire(self, wait=True):
        return self._lock.acquire(wait)

    def release(self):
        self._lock.release()


class BaseBackend(AbstractBackend):
    '''Base dictionary backend without key expiration.'''

    cache = None
    '''A ``dict`` instance.'''

    _lock = None
    '''Lock instance.'''

    def __init__(self, mangler):
        super().__init__(mangler)

        self.cache = {}
        self._lock = Lock(None)

    def lock(self, key):
        return self._lock

    def save(self, key=None, value=None, *, mapping=None, ttl=None):
        if not mapping:
            mapping = {key: value}

        self.cache.update({k: v for k, v in mapping.items()})

    def load(self, keys):
        if self._isScalar(keys):
            return self.cache.get(keys, None)
        else:
            return {k: self.cache[k] for k in keys if k in self.cache}

    def remove(self, keys):
        if self._isScalar(keys):
            keys = (keys,)

        for key in keys:
            self.cache.pop(key, None)

    def clean(self):
        self.cache.clear()

    def dump(self):
        return {k: v for k, v in self.cache.items()}


class Backend(BaseBackend):
    '''
    Test purpose backend implementation. ``save`` and ``delete`` are
    not atomic in general. Though because writes are synchronised it may
    be suitable for limited number of real cases with small cache size.
    '''

    _ttlHeap = None
    '''TTL heap used by the thread to remove the expired entries.'''

    _ttlWatchThread = None
    '''An instance of TTL watcher thread.'''

    _ttlWatchSleep = 1
    '''Seconds for the expiration watcher to sleep in the loop.'''

    _ttlWatchThreadRunning = False
    '''Run flag of the while-loop of the thread.'''

    def __init__(self, mangler):
        super().__init__(mangler)

        self._ttlHeap = []

        self._ttlWatchThread = threading.Thread(target=self._watchExpiry, daemon=True)
        self._ttlWatchThreadRunning = True
        self._ttlWatchThread.start()

    def __del__(self):
        self._ttlWatchThreadRunning = False

    def save(self, key=None, value=None, *, mapping=None, ttl=None):
        super().save(key, value, mapping=mapping, ttl=ttl)

        if ttl:
            for k in mapping or (key,):
                heapq.heappush(self._ttlHeap, (time.time() + ttl, k))

    def clean(self):
        # It touches the heap and needs to be synchronised
        with self._lock:
            super().clean()
            self._ttlHeap.clear()

    def dump(self):
        # It iterates the cache and needs to be synchronised
        with self._lock:
            return super().dump()

    def _watchExpiry(self):
        while self._ttlWatchThreadRunning:
            with self._lock:
                # May contain manually invalidated keys
                expiredKeys = []
                while self._ttlHeap and self._ttlHeap[0][0] < time.time():
                    _, key = heapq.heappop(self._ttlHeap)
                    expiredKeys.append(key)
                self.remove(expiredKeys)

            time.sleep(self._ttlWatchSleep)
