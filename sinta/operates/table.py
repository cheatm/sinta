from sinta.IO import sync
import sinta.codes
import logging


def iterlize(key, default=None):
    if default is None:
        default = lambda: list()

    def wrapper(func):
        def wrapped(*args, **kwargs):
            results = []
            keys = kwargs.get(key, [])
            if len(keys) == 0:
                keys = default()

            for k in keys:
                kwargs[key] = k
                result = func(*args, **kwargs)
                results.append((k, result))
            return results
        return wrapped
    return wrapper


def logger(tag, *keys):
    formatter = "%s | %s" % (tag, " | ".join(["%s"]*(len(keys)+1)))

    def select(*args, **kwargs):
        for key in keys:
            if isinstance(key, int):
                yield args[key]
            else:
                yield kwargs[key]

    def wrapper(func):
        def wrapped(*args, **kwargs):
            show = list(select(*args, **kwargs))
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                show.append(e)
                logging.error(formatter, *show)
            else:
                show.append(result)
                logging.warning(formatter, *show)
                return result
        return wrapped
    return wrapper


class SyncTable(object):

    def __init__(self, collection, manager):
        self.collection = collection
        self.manager = manager

    @iterlize("code", lambda: sinta.codes.STOCKS)
    @logger("insert sync", 'code', "start", "end")
    def insert(self, code, start=None, end=None):
        return sync.insert(self.collection, self.log(code, start, end))

    @iterlize("code", lambda: sinta.codes.STOCKS)
    @logger("update sync", 'code', "start", "end")
    def update(self, code, start=None, end=None):
        return sync.update(self.collection, self.log(code, start, end), upsert=True)

    def log(self, code, start, end):
        return self.manager.get(code).log(start, end)

    @classmethod
    def conf(cls):
        from sinta import config
        from sinta.IO.memory import RootManager
        from pymongo import MongoClient

        db, col = config.LOG_COL.split(".", 1)
        collection = MongoClient(config.MONGODB_URL)[db][col]
        rm = RootManager(config.ROOT)
        return cls(collection, rm)
