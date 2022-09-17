try:
    from CynanBotCommon.lruCache import LruCache
except:
    from lruCache import LruCache


class TestLruCache():

    def test_constructWithNegativeOneCapacity(self):
        lruCache: LruCache = None
        exception: Exception = None

        try:
            lruCache = LruCache(-1)
        except Exception as e:
            exception = e
        
        assert lruCache is None
        assert exception is not None
        assert isinstance(exception, ValueError)

    def test_constructWithOneCapacity(self):
        lruCache: LruCache = None
        exception: Exception = None

        try:
            lruCache = LruCache(1)
        except Exception as e:
            exception = e
        
        assert lruCache is None
        assert exception is not None
        assert isinstance(exception, ValueError)

    def test_constructWithTwoCapacity(self):
        lruCache: LruCache = None
        exception: Exception = None

        try:
            lruCache = LruCache(2)
        except Exception as e:
            exception = e

        assert lruCache is not None
        assert exception is None

    def test_constructWithZeroCapacity(self):
        lruCache: LruCache = None
        exception: Exception = None

        try:
            lruCache = LruCache(0)
        except Exception as e:
            exception = e

        assert lruCache is None
        assert exception is not None
        assert isinstance(exception, ValueError)
