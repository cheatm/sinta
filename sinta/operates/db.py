# encoding:utf-8
from pymongo import MongoClient
from sinta.IO.memory import RootManager, conf_manager
from sinta.operates import resampler
from sinta.IO.mongodb import insert, update, length, read
from sinta.IO.sina import daily_index
from sinta import config
import logging


class FreqStructure:

    def __init__(self, name, res, db, count):
        self.name = name
        self.res = res
        self.db = db
        self.count = count

    def __str__(self):
        return self.name

FREQ = {"H": FreqStructure("H", resampler.min2hour, config.H, 4),
        "D": FreqStructure("D", resampler.min2day, config.D, 1)}


def logger(tag):
    def wrapper(func):
        def wrapped(stock, date):
            try:
                result = func(stock, date)
            except Exception as e:
                logging.error("%s | %s | %s | %s", tag, stock, date, e)
            else:
                logging.warning("%s | %s | %s | %s", tag, stock, date, result)
                return result
        return wrapped
    return wrapper


class DBManager(object):

    def __init__(self, root, uri):
        self.rm = root if isinstance(root, RootManager) else RootManager(root)
        self.client = MongoClient(uri)

    @classmethod
    def conf(cls):
        return cls(conf_manager(), config.MONGODB_URL)

    def check_master(self, codes, start=None, end=None, cover=False):
        for code in codes:
            stock = self.rm.get(code)
            self._check_master(stock, start, end, cover)

    def _check_master(self, stock, start=None, end=None, cover=False):
        try:
            result = self._check(stock, 240, "min1", config.MIN1, start, end, cover)
            stock.flush()
        except Exception as e:
            logging.error('check master | %s | %s-%s | %s ', stock, start, end, e)
        else:
            logging.warning('check master | %s | %s-%s | %s ', stock, start, end, result)

    def _check(self, stock, count, tag, db, start=None, end=None, cover=False):
        collection = self.client[db][self.expand(stock.code)]
        if "datetime_1" not in collection.index_information():
            collection.create_index("datetime", unique=True, background=True)
            logging.warning("%s | create index datetime_1", collection)

        if cover:
            dates = stock.dates(start, end)
        else:
            dates = stock.find({tag: 0}, start, end)

        success = 0
        for date in self._check_date(collection, count, dates):
            stock.fill(date, tag)
            success += 1
        return "%s/%s" % (success, len(dates))

    @staticmethod
    def _check_date(collection, count, dates):
        for date in dates:
            try:
                if length(collection, date) == count:
                    yield date
            except:
                pass

    def write_master(self, codes, start=None, end=None, how="insert", cover=False):
        for code in codes:
            stock = self.rm[code]
            if cover:
                dates = stock.find({"tick": 1}, start, end)
                how="update"
            else:
                dates = stock.find({"tick": 1, 'min1': 0}, start, end)
            for date in dates:
                try:
                    result = self._write_master(stock, date, how)
                except Exception as e:
                    logging.error("min1 | %s | %s | %s | %s", code, date, how, e)
                else:
                    logging.warning("min1 | %s | %s | %s | %s", code, date, how, result)

    def _write_master(self, stock, date, how="insert"):
        write = globals()[how]
        tick = stock.parse(date)
        candle = resampler.tick2min1(tick, date)
        code = self.expand(stock.code)
        return write(self.client[config.MIN1][code], candle)

    def write_freqs(self, freq, codes, start=None, end=None, how="insert", cover=False):
        for f in freq:
            fs = FREQ.get(f, None)
            if fs is None:
                logging.error("Freq: %s not supported" % f)
                continue

            if cover:
                find = {"min1": 1}
                how = "update"
            else:
                find = {"min1": 1, f: 0}
            for code in codes:
                stock = self.rm[code]
                dates = stock.find(find, start, end)
                self.write_freq(fs, code, dates, how)

    def write_freq(self, freq, code, dates, how="insert"):
        if len(dates) == 0:
            logging.warning("%s | %s | empty dates", freq, code)
            return

        col = self.expand(code)
        try:
            data = read(self.client[config.MIN1][col], *dates)
            result = self._write_freq(data, col, freq, how)
        except Exception as e:
            logging.error("%s | %s | %s | %s...%s | %s", freq, code, how, dates[0], dates[-1], e)
        else:
            logging.warning("%s | %s | %s | %s...%s | %s", freq, code, how, dates[0], dates[-1], result)

    def _write_freq(self, data, code, freq, how="insert"):
        write = globals()[how]
        candle = freq.res(data)
        return write(self.client[freq.db][code], candle)

    def check_freq(self, freq, codes, start=None, end=None, cover=False):
        for f in freq:
            fs = FREQ.get(f, None)
            if fs is None:
                logging.error("Freq: %s not supported" % f)
                continue

            for code in codes:
                stock = self.rm.get(code)
                self._check_freq(stock, fs, start, end, cover)

    def _check_freq(self, stock, fs, start=None, end=None, cover=False):
        try:
            result = self._check(stock, fs.count, fs.name, fs.db, start, end, cover)
            stock.flush()
        except Exception as e:
            logging.error('check %s | %s | %s-%s | %s ', fs.name, stock, start, end, e)
        else:
            logging.warning('check %s | %s | %s-%s | %s ', fs.name, stock, start, end, result)

    @staticmethod
    def expand(code):
        if code.startswith("6"):
            return code + ".XSHG"
        else:
            return code + ".XSHE"

    def save_indexes(self, code, start="", end=""):
        for c in code:
            self.save_indexes(c, start, end)

    def save_index(self, code, start="", end=""):
        try:
            name = code[:6]
            data = daily_index(name, start, end)
            result = update(self.client[config.D][code], data)
        except Exception as e:
            logging.error("idx | %s | %s", code, e)
        else:
            logging.warning("idx | %s | %s", code, result)