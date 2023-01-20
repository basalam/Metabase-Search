import time
import pickle
import threading

from .. import test, Hermes, Mangler
from ..backend import redis, AbstractLock


class TestRedis(test.TestCase):
    def setUp(self):
        self.testee = Hermes(redis.Backend, ttl=360, lockTimeout=120)
        self.fixture = test.createFixture(self.testee)

        self.testee.clean()

    def tearDown(self):
        self.testee.clean()

    def testSimple(self):
        self.assertEqual(0, self.fixture.calls)
        self.assertEqual(0, self.testee.backend.client.dbsize())

        key = "cache:entry:hermes.test:Fixture:simple:" + self._arghash(
            "alpha", b="beta"
        )
        for _ in range(4):
            self.assertEqual("ateb+ahpla", self.fixture.simple("alpha", b="beta"))
            self.assertEqual(1, self.fixture.calls)
            self.assertEqual(1, self.testee.backend.client.dbsize())

            self.assertEqual(360, self.testee.backend.client.ttl(key))
            self.assertEqual(
                "ateb+ahpla", pickle.loads(self.testee.backend.client.get(key))
            )

        self.fixture.simple.invalidate("alpha", b="beta")
        self.assertEqual(0, self.testee.backend.client.dbsize())

        expected = "]}'ammag'{[+}]'ateb'[ :'ahpla'{"
        key = "cache:entry:hermes.test:Fixture:simple:{}".format(
            self._arghash({"alpha": ["beta"]}, [{"gamma"}])
        )
        for _ in range(4):
            self.assertEqual(
                expected, self.fixture.simple({"alpha": ["beta"]}, [{"gamma"}])
            )

            self.assertEqual(2, self.fixture.calls)
            self.assertEqual(1, self.testee.backend.client.dbsize())

            self.assertEqual(360, self.testee.backend.client.ttl(key))

            self.assertEqual(
                expected, pickle.loads(self.testee.backend.client.get(key))
            )

    def testTagged(self):
        self.assertEqual(0, self.fixture.calls)
        self.assertEqual(0, self.testee.backend.client.dbsize())

        for _ in range(4):
            self.assertEqual("ae-hl", self.fixture.tagged("alpha", b="beta"))
            self.assertEqual(1, self.fixture.calls)
            self.assertEqual(3, self.testee.backend.client.dbsize())

            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:rock"))
            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:tree"))
            rockTag = pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
            treeTag = pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
            self.assertFalse(rockTag == treeTag)
            self.assertEqual(16, len(rockTag))
            self.assertEqual(16, len(treeTag))

            argHash = self._arghash("alpha", b="beta")
            tagHash = self.testee.mangler.hashTags(dict(tree=treeTag, rock=rockTag))
            key = "cache:entry:hermes.test:Fixture:tagged:{0}:{1}".format(
                argHash, tagHash
            )
            self.assertEqual(360, self.testee.backend.client.ttl(key))
            self.assertEqual("ae-hl", pickle.loads(self.testee.backend.client.get(key)))

        self.fixture.tagged.invalidate("alpha", b="beta")

        self.assertEqual(2, self.testee.backend.client.dbsize())

        rockTag = pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
        treeTag = pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
        self.assertNotEqual(rockTag, treeTag)
        self.assertEqual(16, len(rockTag))
        self.assertEqual(16, len(treeTag))

        for _ in range(4):
            self.assertEqual("ae-hl", self.fixture.tagged("alpha", "beta"))
            self.assertEqual("ae%hl", self.fixture.tagged2("alpha", "beta"))
            self.assertEqual(3, self.fixture.calls)

            self.assertEqual(5, self.testee.backend.client.dbsize())
            self.assertEqual(
                rockTag, pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
            )
            self.assertEqual(
                treeTag, pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
            )
            self.assertEqual(
                16, len(pickle.loads(self.testee.backend.client.get("cache:tag:ice")))
            )

        self.testee.clean(["rock"])

        self.assertEqual(4, self.testee.backend.client.dbsize())
        self.assertIsNone(self.testee.backend.client.get("cache:tag:rock"))
        iceTag = pickle.loads(self.testee.backend.client.get("cache:tag:ice"))

        for _ in range(4):
            self.assertEqual("ae-hl", self.fixture.tagged("alpha", "beta"))
            self.assertEqual("ae%hl", self.fixture.tagged2("alpha", "beta"))
            self.assertEqual(5, self.fixture.calls)

            size = self.testee.backend.client.dbsize()
            self.assertEqual(
                7, size, "has new and old entries for tagged and tagged 2 + 3 tags"
            )
            self.assertEqual(
                treeTag, pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
            )
            self.assertEqual(
                iceTag, pickle.loads(self.testee.backend.client.get("cache:tag:ice"))
            )
            self.assertEqual(
                16, len(pickle.loads(self.testee.backend.client.get("cache:tag:rock")))
            )
            self.assertNotEqual(
                rockTag, pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
            )

    def testFunction(self):
        counter = dict(foo=0, bar=0)

        @self.testee
        def foo(a, b):
            counter["foo"] += 1
            return "{0}+{1}".format(a, b)[::-1]

        key = lambda fn, *args, **kwargs: "mk:{0}:{1}".format(*args)

        @self.testee(tags=("a", "z"), key=key, ttl=120)
        def bar(a, b):
            counter["bar"] += 1
            return "{0}-{1}".format(a, b)[::2]

        self.assertEqual(0, counter["foo"])
        self.assertEqual(0, self.testee.backend.client.dbsize())

        key = "cache:entry:hermes.test.redis:foo:" + self._arghash("alpha", "beta")
        for _ in range(4):
            self.assertEqual("ateb+ahpla", foo("alpha", "beta"))

            self.assertEqual(1, counter["foo"])
            self.assertEqual(1, self.testee.backend.client.dbsize())

            self.assertEqual(360, self.testee.backend.client.ttl(key))
            self.assertEqual(
                "ateb+ahpla", pickle.loads(self.testee.backend.client.get(key))
            )

        foo.invalidate("alpha", "beta")
        self.assertFalse(self.testee.backend.client.exists(key))
        self.assertEqual(0, self.testee.backend.client.dbsize())

        self.assertEqual(0, counter["bar"])
        self.assertEqual(0, self.testee.backend.client.dbsize())

        for _ in range(4):
            self.assertEqual("apabt", bar("alpha", "beta"))
            self.assertEqual(1, counter["bar"])
            self.assertEqual(3, self.testee.backend.client.dbsize())

            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:a"))
            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:z"))

            aTag = pickle.loads(self.testee.backend.client.get("cache:tag:a"))
            zTag = pickle.loads(self.testee.backend.client.get("cache:tag:z"))
            self.assertFalse(aTag == zTag)
            self.assertEqual(16, len(aTag))
            self.assertEqual(16, len(zTag))

            tagHash = self.testee.mangler.hashTags(dict(a=aTag, z=zTag))
            key = "mk:alpha:beta:" + tagHash
            self.assertEqual(120, self.testee.backend.client.ttl(key))
            self.assertEqual("apabt", pickle.loads(self.testee.backend.client.get(key)))

        bar.invalidate("alpha", "beta")
        self.assertEqual(1, counter["foo"])
        self.assertIsNone(self.testee.backend.client.get(key))
        self.assertEqual(2, self.testee.backend.client.dbsize())

        self.assertEqual("apabt", bar("alpha", "beta"))
        self.assertEqual(2, counter["bar"])
        self.assertEqual(3, self.testee.backend.client.dbsize())

    def testKey(self):
        self.assertEqual(0, self.fixture.calls)
        self.assertEqual(0, self.testee.backend.client.dbsize())

        for _ in range(4):
            self.assertEqual("apabt", self.fixture.key("alpha", "beta"))
            self.assertEqual(1, self.fixture.calls)
            self.assertEqual(3, self.testee.backend.client.dbsize())

            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:ash"))
            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:stone"))
            ashTag = pickle.loads(self.testee.backend.client.get("cache:tag:ash"))
            stoneTag = pickle.loads(self.testee.backend.client.get("cache:tag:stone"))
            self.assertFalse(ashTag == stoneTag)
            self.assertEqual(16, len(ashTag))
            self.assertEqual(16, len(stoneTag))

            tagHash = self.testee.mangler.hashTags(dict(ash=ashTag, stone=stoneTag))
            key = "mykey:alpha:beta:" + tagHash
            self.assertEqual(360, self.testee.backend.client.ttl(key))
            self.assertEqual("apabt", pickle.loads(self.testee.backend.client.get(key)))

        self.fixture.key.invalidate("alpha", "beta")

        self.assertIsNone(self.testee.backend.client.get(key))
        self.assertEqual(2, self.testee.backend.client.dbsize())

        self.assertEqual(
            ashTag, pickle.loads(self.testee.backend.client.get("cache:tag:ash"))
        )
        self.assertEqual(
            stoneTag, pickle.loads(self.testee.backend.client.get("cache:tag:stone"))
        )

    def testAll(self):
        self.assertEqual(0, self.fixture.calls)
        self.assertEqual(0, self.testee.backend.client.dbsize())
        for _ in range(4):
            self.assertEqual(
                {"a": 1, "b": {"b": "beta"}}, self.fixture.all({"alpha": 1}, ["beta"])
            )
            self.assertEqual(1, self.fixture.calls)
            self.assertEqual(3, self.testee.backend.client.dbsize())

            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:a"))
            self.assertEqual(-1, self.testee.backend.client.ttl("cache:tag:z"))

            aTag = pickle.loads(self.testee.backend.client.get("cache:tag:a"))
            zTag = pickle.loads(self.testee.backend.client.get("cache:tag:z"))
            self.assertFalse(aTag == zTag)
            self.assertEqual(16, len(aTag))
            self.assertEqual(16, len(zTag))

            tagHash = self.testee.mangler.hashTags(dict(a=aTag, z=zTag))
            key = "mk:{'alpha':1}:['beta']:" + tagHash
            self.assertEqual(1200, self.testee.backend.client.ttl(key))
            self.assertEqual(
                {"a": 1, "b": {"b": "beta"}},
                pickle.loads(self.testee.backend.client.get(key)),
            )

        self.fixture.all.invalidate({"alpha": 1}, ["beta"])

        self.assertEqual(2, self.testee.backend.client.dbsize())
        self.assertEqual(
            aTag, pickle.loads(self.testee.backend.client.get("cache:tag:a"))
        )
        self.assertEqual(
            zTag, pickle.loads(self.testee.backend.client.get("cache:tag:z"))
        )

    def testClean(self):
        self.assertEqual(0, self.fixture.calls)
        self.assertEqual(0, self.testee.backend.client.dbsize())

        self.assertEqual("ateb+ahpla", self.fixture.simple("alpha", "beta"))
        self.assertEqual("aldamg", self.fixture.tagged("gamma", "delta"))
        self.assertEqual(2, self.fixture.calls)
        self.assertEqual(4, self.testee.backend.client.dbsize())

        self.testee.clean()

        self.assertEqual(2, self.fixture.calls)
        self.assertEqual(0, self.testee.backend.client.dbsize())

    def testCleanTagged(self):
        self.assertEqual(0, self.fixture.calls)
        self.assertEqual(0, self.testee.backend.client.dbsize())

        self.assertEqual("ateb+ahpla", self.fixture.simple("alpha", "beta"))
        self.assertEqual("aldamg", self.fixture.tagged("gamma", "delta"))
        self.assertEqual(2, self.fixture.calls)
        self.assertEqual(4, self.testee.backend.client.dbsize())

        simpleKey = "cache:entry:hermes.test:Fixture:simple:" + self._arghash(
            "alpha", "beta"
        )
        self.assertEqual(
            "ateb+ahpla", pickle.loads(self.testee.backend.client.get(simpleKey))
        )

        rockTag = pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
        treeTag = pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
        self.assertFalse(rockTag == treeTag)
        self.assertEqual(16, len(rockTag))
        self.assertEqual(16, len(treeTag))

        argHash = self._arghash("gamma", "delta")
        tagHash = self.testee.mangler.hashTags(dict(tree=treeTag, rock=rockTag))
        taggedKey = "cache:entry:hermes.test:Fixture:tagged:{0}:{1}".format(
            argHash, tagHash
        )
        self.assertEqual(
            "aldamg", pickle.loads(self.testee.backend.client.get(taggedKey))
        )

        self.testee.clean(("rock",))
        self.assertEqual(3, self.testee.backend.client.dbsize())

        self.assertEqual(
            "ateb+ahpla", pickle.loads(self.testee.backend.client.get(simpleKey))
        )

        self.assertIsNone(self.testee.backend.client.get("cache:tag:rock"))
        self.assertEqual(
            treeTag, pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
        )

        # stale still accessible, though only directly
        self.assertEqual(
            "aldamg", pickle.loads(self.testee.backend.client.get(taggedKey))
        )

        self.assertEqual("ateb+ahpla", self.fixture.simple("alpha", "beta"))
        self.assertEqual("aldamg", self.fixture.tagged("gamma", "delta"))
        self.assertEqual(3, self.fixture.calls)
        self.assertEqual(5, self.testee.backend.client.dbsize(), "+1 old tagged entry")

        self.assertEqual(
            "ateb+ahpla", pickle.loads(self.testee.backend.client.get(simpleKey))
        )

        self.assertNotEqual(
            rockTag, pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
        )
        rockTag = pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
        self.assertFalse(rockTag == treeTag)
        self.assertEqual(16, len(rockTag))
        self.assertEqual(
            treeTag, pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
        )

        # stale still accessible, though only directly
        self.assertEqual(
            "aldamg", pickle.loads(self.testee.backend.client.get(taggedKey))
        )

        argHash = self._arghash("gamma", "delta")
        tagHash = self.testee.mangler.hashTags(dict(tree=treeTag, rock=rockTag))
        taggedKey = "cache:entry:hermes.test:Fixture:tagged:{0}:{1}".format(
            argHash, tagHash
        )
        self.assertEqual(
            "aldamg", pickle.loads(self.testee.backend.client.get(taggedKey))
        )

        self.testee.clean(("rock", "tree"))
        self.assertEqual(
            3, self.testee.backend.client.dbsize(), "simaple, new tagged and old tagged"
        )

        self.assertEqual(
            "ateb+ahpla", pickle.loads(self.testee.backend.client.get(simpleKey))
        )

        # new stale is accessible, though only directly
        self.assertEqual(
            "aldamg", pickle.loads(self.testee.backend.client.get(taggedKey))
        )

        self.assertEqual("ateb+ahpla", self.fixture.simple("alpha", "beta"))
        self.assertEqual("aldamg", self.fixture.tagged("gamma", "delta"))
        self.assertEqual(4, self.fixture.calls)
        self.assertEqual(
            6, self.testee.backend.client.dbsize(), "+2 old tagged entries"
        )

        self.assertEqual(
            "ateb+ahpla", pickle.loads(self.testee.backend.client.get(simpleKey))
        )

        # new stale still accessible, though only directly
        self.assertEqual(
            "aldamg", pickle.loads(self.testee.backend.client.get(taggedKey))
        )

        self.assertNotEqual(
            rockTag, pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
        )
        self.assertNotEqual(
            treeTag, pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
        )

        rockTag = pickle.loads(self.testee.backend.client.get("cache:tag:rock"))
        treeTag = pickle.loads(self.testee.backend.client.get("cache:tag:tree"))
        self.assertFalse(rockTag == treeTag)
        self.assertEqual(16, len(rockTag))
        self.assertEqual(16, len(treeTag))

        argHash = self._arghash("gamma", "delta")
        tagHash = self.testee.mangler.hashTags(dict(tree=treeTag, rock=rockTag))
        taggedKey = "cache:entry:hermes.test:Fixture:tagged:{0}:{1}".format(
            argHash, tagHash
        )
        self.assertEqual(
            "aldamg", pickle.loads(self.testee.backend.client.get(taggedKey))
        )

        self.testee.clean(("rock", "tree"))
        self.testee.clean()
        self.assertEqual(0, self.testee.backend.client.dbsize())

    def testNested(self):
        self.assertEqual("beta+alpha", self.fixture.nested("alpha", "beta"))
        self.assertEqual(2, self.fixture.calls)
        key = "cache:entry:hermes.test:Fixture:nested:" + self._arghash("alpha", "beta")
        self.assertEqual(
            "beta+alpha", pickle.loads(self.testee.backend.client.get(key))
        )
        key = "cache:entry:hermes.test:Fixture:simple:" + self._arghash("beta", "alpha")
        self.assertEqual(
            "ahpla+ateb", pickle.loads(self.testee.backend.client.get(key))
        )

    def testConcurrent(self):
        log = []
        key = lambda fn, *args, **kwargs: "mk:{0}:{1}".format(*args)

        @self.testee(tags=("a", "z"), key=key, ttl=120)
        def bar(a, b):
            log.append(1)
            time.sleep(0.04)
            return "{0}-{1}".format(a, b)[::2]

        threads = [
            threading.Thread(target=bar, args=("alpha", "beta")) for _ in range(4)
        ]
        tuple(map(threading.Thread.start, threads))
        tuple(map(threading.Thread.join, threads))

        self.assertEqual(1, sum(log))
        self.assertEqual(3, self.testee.backend.client.dbsize())

        aTag = pickle.loads(self.testee.backend.client.get("cache:tag:a"))
        zTag = pickle.loads(self.testee.backend.client.get("cache:tag:z"))
        self.assertFalse(aTag == zTag)
        self.assertEqual(16, len(aTag))
        self.assertEqual(16, len(zTag))

        tagHash = self.testee.mangler.hashTags(dict(a=aTag, z=zTag))
        key = "mk:alpha:beta:" + tagHash
        self.assertEqual("apabt", pickle.loads(self.testee.backend.client.get(key)))

        del log[:]
        self.testee.clean()
        self.testee.backend.lock = lambda k: AbstractLock(k)  # now see a dogpile

        threads = [
            threading.Thread(target=bar, args=("alpha", "beta")) for _ in range(4)
        ]
        tuple(map(threading.Thread.start, threads))
        tuple(map(threading.Thread.join, threads))

        self.assertGreater(sum(log), 1, "dogpile")
        # enries may be duplicated if tags overwrite
        self.assertGreaterEqual(self.testee.backend.client.dbsize(), 3)

        aTag = pickle.loads(self.testee.backend.client.get("cache:tag:a"))
        zTag = pickle.loads(self.testee.backend.client.get("cache:tag:z"))
        self.assertFalse(aTag == zTag)
        self.assertEqual(16, len(aTag))
        self.assertEqual(16, len(zTag))

        tagHash = self.testee.mangler.hashTags(dict(a=aTag, z=zTag))
        key = "mk:alpha:beta:" + tagHash
        self.assertEqual("apabt", pickle.loads(self.testee.backend.client.get(key)))

    def testLazyInit(self):
        server = test.FakeBackendServer()
        server.serve()

        Hermes(redis.Backend, port=server.port)

        server.close()
        self.assertEqual([], server.log)


class TestRedisLock(test.TestCase):
    def setUp(self):
        cache = Hermes(redis.Backend)
        cache.clean()

        self.testee = redis.Lock("123", cache.backend.client)

    def testAcquire(self):
        for _ in range(2):
            try:
                self.assertTrue(self.testee.acquire(True))
                self.assertFalse(self.testee.acquire(False))
                self.assertEqual("123", self.testee.key)
                self.assertEqual(900, self.testee.client.ttl(self.testee.key))
            finally:
                self.testee.release()

    def testRelease(self):
        for _ in range(2):
            try:
                self.assertTrue(self.testee.acquire(True))
                self.assertFalse(self.testee.acquire(False))
                self.assertEqual("123", self.testee.key)
            finally:
                self.testee.release()
                self.assertIs(None, self.testee.client.get(self.testee.key))

    def testWith(self):
        with self.testee:
            self.assertFalse(self.testee.acquire(False))
            self.assertEqual("123", self.testee.key)

            client = redis.Backend(Mangler()).client
            another = redis.Lock("234", client)
            with another:
                self.assertFalse(another.acquire(False))
                self.assertFalse(self.testee.acquire(False))
                self.assertEqual("234", another.key)

    def testConcurrent(self):
        log = []
        check = threading.Lock()

        def target():
            with self.testee:
                log.append(check.acquire(False))
                time.sleep(0.05)
                check.release()
                time.sleep(0.05)

        threads = tuple(map(lambda i: threading.Thread(target=target), range(4)))
        tuple(map(threading.Thread.start, threads))
        tuple(map(threading.Thread.join, threads))

        self.assertEqual([True] * 4, log)
