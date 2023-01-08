import os
import types
import pickle
import hashlib
import inspect
import binascii
import functools

from .backend import AbstractBackend

__all__ = "Hermes", "Mangler"


class Mangler:
    """Key manager responsible for creating keys, hashing and serialisation."""

    prefix = "cache"
    """Prefix for cache and tag entries."""

    def hash(self, value):
        return hashlib.md5(value).hexdigest()[::2]  # full md5 seems too long

    def dumps(self, value):
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    def loads(self, value):
        return pickle.loads(value)

    def nameEntry(self, fn, *args, **kwargs):
        """
        Return cache key for given callable and its positional and
        keyword arguments.

        Note how callable, ``fn``, is represented in the cache key:

          1) a ``types.MethodType`` instance -> names of
             ``(module, class, method)``
          2) a ``types.FunctionType`` instance -> names of
             ``(module, function)``
          3) other callalbe objects with ``__name__`` -> name of
             ``(module, object)``

        This means that if two function are defined dynamically in the
        same module with same names, like::

          def createF1():
              @cache
              def f(a, b):
                  return a + b
              return f

          def createF2():
              @cache
              def f(a, b):
                  return a * b
              return f

          print(createF1()(1, 2))
          print(createF2()(1, 2))

        Both will return `3`, because cache keys will clash. In such cases
        you need to pass ``key`` with custom key function.

        It can also be that an object in case 3 doesn't have name, or its
        name isn't unique, then a ``nameEntry`` should be overridden with
        something that represents it uniquely, like
        ``repr(fn).rsplit(' at 0x', 1)[0]`` (address should be stripped so
        after Python process restart the cache can still be valid
        and usable).
        """

        result = [self.prefix, "entry"]
        if callable(fn):
            try:
                # types.MethodType
                result.extend(
                    [fn.__module__, fn.__self__.__class__.__name__, fn.__name__]
                )
            except AttributeError:
                try:
                    # types.FunctionType and other object with __name__
                    result.extend([fn.__module__, fn.__name__])
                except AttributeError:
                    raise TypeError(
                        "Fn is callable but its name is undefined, consider overriding Mangler.nameEntry"
                    )
        else:
            raise TypeError("Fn is expected to be callable")

        arguments = args, tuple(sorted(kwargs.items()))
        result.append(self.hash(self.dumps(arguments)))

        return ":".join(result)

    def nameTag(self, tag):
        return ":".join([self.prefix, "tag", tag])

    def mapTags(self, tagKeys):
        hash = binascii.hexlify(os.urandom(4)).decode("ascii")
        return {key: self.hash(":".join((key, hash)).encode("utf8")) for key in tagKeys}

    def hashTags(self, tagMap):
        values = tuple(zip(*sorted(tagMap.items())))[1]  # sorted by key dict values
        return self.hash(":".join(values).encode("utf8"))

    def nameLock(self, entryKey):
        parts = entryKey.split(":")
        if parts[0] == self.prefix:
            entryKey = ":".join(parts[2:])
        return ":".join([self.prefix, "lock", entryKey])


class Cached:
    """A cache-point wrapper for callables and descriptors."""

    _frontend = None
    """
    Hermes instance which provides backend and mangler instances, and
    TTL fallback value.
    """

    _callable = None
    """
    The decorated callable, stays ``types.FunctionType`` if a function
    is decorated, otherwise it is transformed to ``types.MethodType``
    on the instance clone by descriptor protocol implementation. It can
    also be a method descriptor which is also transformed accordingly to
    the descriptor protocol (e.g. ``staticmethod`` and ``classmethod``).
    """

    _isDescriptor = None
    """Flag defining if the callable is a method descriptor."""

    _isMethod = None
    """Flag defining if the callable is a method."""

    _ttl = None
    """Cache entry Time To Live for decorated callable."""

    _keyFunc = None
    """Key creation function."""

    _tags = None
    """Cache entry tags for decorated callable."""

    def __init__(self, frontend, callable, *, ttl=None, key=None, tags=None):
        self._frontend = frontend
        self._ttl = ttl
        self._keyFunc = key
        self._tags = tags

        self._callable = callable
        self._isDescriptor = inspect.ismethoddescriptor(callable)
        self._isMethod = inspect.ismethod(callable)

        # preserve ``__name__``, ``__doc__``, etc
        functools.update_wrapper(self, callable)

    def _load(self, key):
        if self._tags:
            tagMap = self._frontend.backend.load(
                map(self._frontend.mangler.nameTag, self._tags)
            )
            if len(tagMap) != len(self._tags):
                return None
            else:
                key += ":" + self._frontend.mangler.hashTags(tagMap)

        return self._frontend.backend.load(key)

    def _save(self, key, value):
        if self._tags:
            namedTags = tuple(map(self._frontend.mangler.nameTag, self._tags))
            tagMap = self._frontend.backend.load(namedTags)
            missingTags = set(namedTags) - set(tagMap.keys())
            if missingTags:
                missingTagMap = self._frontend.mangler.mapTags(missingTags)
                self._frontend.backend.save(mapping=missingTagMap, ttl=None)
                tagMap.update(missingTagMap)
                assert len(self._tags) == len(tagMap)

            key += ":" + self._frontend.mangler.hashTags(tagMap)

        ttl = self._ttl if self._ttl is not None else self._frontend.ttl

        if value is not None and (
            (isinstance(value, list) and len(value) > 0) or not isinstance(value, list)
        ):
            return self._frontend.backend.save(key, value, ttl=ttl)

    def _remove(self, key):
        if self._tags:
            tagMap = self._frontend.backend.load(
                map(self._frontend.mangler.nameTag, self._tags)
            )
            if len(tagMap) != len(self._tags):
                return
            else:
                key += ":" + self._frontend.mangler.hashTags(tagMap)

        self._frontend.backend.remove(key)

    def _key(self, *args, **kwargs):
        return (self._keyFunc or self._frontend.mangler.nameEntry)(
            self._callable, *args, **kwargs
        )

    def invalidate(self, *args, **kwargs):
        try:
            self._remove(self._key(*args, **kwargs))
        except Exception as ex:
            raise (ex)

    def __call__(self, *args, **kwargs):
        try:
            key = self._key(*args, **kwargs)
            value = self._load(key)
            if value is None:
                with self._frontend.backend.lock(key):
                    # it's better to read twice than lock every read
                    value = self._load(key)
                    if value is None:
                        value = self._callable(*args, **kwargs)
                        self._save(key, value)
            return value
        except Exception as ex:
            return self._callable(*args, **kwargs)

    def __get__(self, instance, type):
        """
        Implements non-data descriptor protocol.

        The invocation happens only when instance method is decorated,
        so we can distinguish between decorated ``types.MethodType`` and
        ``types.FunctionType``. Python class declaration mechanics prevent
        a decorator from having awareness of the class type, as the
        function is received by the decorator before it becomes an
        instance method.

        How it works::

          cache = hermes.Hermes()

          class Model:

            @cache
            def calc(self):
              return 42

          m = Model()
          m.calc

        Last attribute access results in the call, ``calc.__get__(m, Model)``,
        where ``calc`` is instance of ``hermes.Cached`` which decorates the
        original ``Model.calc``.

        Note, initially ``hermes.Cached`` is created on decoration per
        class method, when class type is created by the interpreter, and
        is shared among all instances. Later, on attribute access, a copy
        is returned with bound ``_callable``, just like ordinary Python
        method descriptor works.

        For more details, `descriptor-protocol
        <http://docs.python.org/3/howto/descriptor.html#descriptor-protocol>`_.
        """

        if instance is None:
            return self
        elif self._isDescriptor:
            return self._copy(self._callable.__get__(instance, type))
        elif not self._isMethod:
            return self._copy(types.MethodType(self._callable, instance))
        else:
            return self

    def _copy(self, callable):
        """
        Create a shallow copy of self with ``_callable``
        replaced to given instance.
        """

        boundCached = object.__new__(self.__class__)
        boundCached.__dict__ = self.__dict__.copy()
        boundCached._callable = callable
        return boundCached


class Hermes:
    """
    Cache facade. Usage::

      import hermes.backend.redis

      cache = hermes.Hermes(
        hermes.backend.redis.Backend, ttl = 600, host = 'localhost', db = 1)


      @cache
      def foo(a, b):
        return a * b

      class Example:

        @cache(tags = ('math', 'power'), ttl = 1200)
        def bar(self, a, b):
          return a ** b

        @cache(tags = ('math', 'avg'),
          key = lambda fn, *args, **kwargs: 'avg:{0}:{1}'.format(*args))
        def baz(self, a, b):
          return (a + b) / 2.0


      print(foo(2, 333))

      example = Example()
      print(example.bar(2, 10))
      print(example.baz(2, 10))

      foo.invalidate(2, 333)
      example.bar.invalidate(2, 10)
      example.baz.invalidate(2, 10)

      cache.clean(['math']) # invalidate entries tagged 'math'
      cache.clean()         # flush cache

    """

    backend = None
    """Cache backend."""

    mangler = None
    """Key manager responsible for creating keys, hashing and serialisation."""

    cachedClass = None
    """Class of cache-point callable object."""

    ttl = 3600
    """Default cache entry time-to-live."""

    def __init__(
        self,
        backendClass=AbstractBackend,
        *,
        manglerClass=Mangler,
        cachedClass=Cached,
        ttl=None,
        **backendOptions
    ):
        """
        Initialises the cache decorator factory.

        Positional arguments are backend class and mangler class. If
        omitted noop-backend and built-in mangler will be be used.

        Keyword arguments comprise of ``ttl`` and backend parameters.
        """

        self.ttl = ttl if ttl is not None else self.ttl

        assert issubclass(manglerClass, Mangler)
        self.mangler = manglerClass()

        assert issubclass(backendClass, AbstractBackend)
        self.backend = backendClass(self.mangler, **backendOptions)

        assert issubclass(cachedClass, Cached)
        self.cachedClass = cachedClass

    def __call__(self, *args, ttl=None, tags=None, key=None):
        """
        Decorator that caches method or function result. The following key
        arguments are optional:

          :key:   Lambda that provides custom key, otherwise ``Mangler.nameEntry`` is used.
          :ttl:   Seconds until entry expiration, otherwise instance default is used.
          :tags:  Cache entry tag list.

        ``@cache`` decoration is supported as well as
        ``@cache(ttl = 7200, tags = ('tag1', 'tag2'), key = lambda fn, *args, **kwargs: 'mykey')``.
        """

        if args:
            # @cache
            if callable(args[0]) or inspect.ismethoddescriptor(args[0]):
                return self.cachedClass(self, args[0])
            else:
                raise TypeError(
                    "First positional argument must be callable or method descriptor"
                )
        else:
            # @cache()
            return lambda fn: self.cachedClass(self, fn, ttl=ttl, tags=tags, key=key)

    def clean(self, tags=None):
        """
        If tags argument is omitted flushes all entries, otherwise removes
        provided tag entries.
        """
        try:
            if tags:
                self.backend.remove(map(self.mangler.nameTag, tags))
            else:
                self.backend.clean()
        except Exception as ex:
            raise (ex)
