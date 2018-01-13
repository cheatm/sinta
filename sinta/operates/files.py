from sinta.IO.memory import RootManager, StockDir, conf_manager
from sinta.IO.sina import history_tick, daily, SinaBreak, SinaNoData
import logging
from time import sleep

STATUS = ['tick', "min1", "H", "D"]


def expand(code):
    if code.startswith("6"):
        return "sh" + code
    else:
        return "sz" + code


class IndexManager(object):

    def __init__(self, root):
        self.rm = root if isinstance(root, RootManager) else RootManager(root)

    @classmethod
    def conf(cls):
        return cls(conf_manager())

    @staticmethod
    def get_index(code, start="", end=""):
        data = daily(code, start, end)
        for status in STATUS:
            data[status] = 0
        return data

    def create_index(self, code, start="", end="", cover=False):
        stock = self.rm.get(code)
        if cover or not stock.has_index:
            index = self.get_index(code, start, end)
            stock.index = index
            stock.flush()
        return stock.index

    def create_indexes(self, codes, start="", end="", cover=False):
        for code in codes:
            try:
                index = self.create_index(code, start, end, cover)
            except Exception as e:
                logging.error('%s | %s-%s | %s', code, start, end, e)
            else:
                logging.warning('%s | %s-%s | %s', code, start, end, len(index))

    def update_index(self, code, start="", end=""):
        index = self.get_index(code, start, end)
        stock = self.rm.get(code)
        stock.update(index)
        stock.flush()
        return stock.index

    def update_indexes(self, codes, start="", end=""):
        for code in codes:
            try:
                index = self.update_index(code, start, end)
            except Exception as e:
                logging.error('%s | %s-%s | %s', code, start, end, e)
            else:
                logging.warning('%s | %s-%s | %s', code, start, end, len(index))

    def require(self, stock, date):
        if not isinstance(stock, StockDir):
            if isinstance(stock, str):
                stock = self.rm[stock]
            else:
                return 0

        code = stock.code
        stock[date] = history_tick(expand(code), date)
        return 1

    def requires(self, iterable):
        for stock, date in iterable:
            try:
                status = self.require(stock, date)
            except SinaBreak:
                seconds = 2*60
                logging.error("require | %s | %s | %s", stock, date, "SinaBreak sleep for %s seconds" % seconds)
                sleep(seconds)
            except Exception as e:
                logging.error("require | %s | %s | %s", stock, date, e)
            else:
                logging.warning("require | %s | %s | %s", stock, date, status)
            sleep(1)

    def require_range(self, stocks, start, end):
        self.requires(self._require_range(stocks, start, end))

    def _require_range(self, stocks, start, end):
        for code in stocks:
            stock = self.rm[code]
            for date in stock.find_dates("tick", 0, slice(start, end)):
                yield stock, date

    def has_index(self, code):
        return self.rm[code].has_index

    def delete(self, codes, start=None, end=None):
        for code in codes:
            try:
                deleted = self.rm.delete(code, start, end)
                count = len(deleted)
            except Exception as e:
                logging.error("delete tick | %s | %s-%s | %s ", code, start, end, e)
            else:
                logging.warning("delete tick | %s | %s-%s | %s ", code, start, end, count)