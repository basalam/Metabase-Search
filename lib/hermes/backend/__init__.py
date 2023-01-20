import collections.abc


class AbstractLock:
    """
    Base locking class. Implements context manger protocol. Mocks
    ``acquire`` and ``release`` i.e. it always acquires.
    """

    key = None
    """Implementation may be key-aware."""

    def __init__(self, key):
        self.key = key

    def __enter__(self):
        self.acquire()

    def __exit__(self, type, value, traceback):
        self.release()

    def acquire(self, wait=True):
        return True

    def release(self):
        pass


class AbstractBackend:
    """Abstract backend."""

    mangler = None
    """Key manager responsible for creating keys, hashing and serialisation."""

    def __init__(self, mangler):
        self.mangler = mangler

    @classmethod
    def _isScalar(cls, value):
        return not isinstance(value, collections.abc.Iterable) or isinstance(
            value, (bytes, str)
        )

    def lock(self, key):
        return AbstractLock(self.mangler.nameLock(key))

    def save(self, key=None, value=None, *, mapping=None, ttl=None):
        pass

    def load(self, keys):
        """
        Note, when handling a multiple key call, absent value keys
        should be excluded from resulting dictionary.
        """

        return None if self._isScalar(keys) else {}

    def remove(self, keys):
        pass

    def clean(self):
        pass
