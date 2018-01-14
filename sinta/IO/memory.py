import os
import pandas as pd
from datetime import datetime
from functools import partial
from sinta import config
import logging


class StockDir(object):

    def __init__(self, root, code):
        self.root = root
        self.code = code
        self.index_path = os.path.join(self.root, 'index.csv')
        if self.has_index:
            self.index = pd.read_csv(self.index_path, index_col="date")
        else:
            self.index = pd.DataFrame()

    def __str__(self):
        return self.code

    @property
    def has_index(self):
        return os.path.isfile(self.index_path)

    def _not_exist(self, value):
        return value not in self.index.index

    def update(self, frame):
        bools = list(map(self._not_exist, frame.index))
        self.index = pd.concat([self.index, frame[bools]]).sort_index()

    def flush(self):
        self.index.to_csv(self.index_path)

    def tick_path(self, date):
        return os.path.join(self.root, '%s.csv' % date)

    def parse(self, date):
        return self.__getitem__(date).rename_axis(partial(self.trans, date)).sort_index()

    @staticmethod
    def trans(date, time):
        return datetime.strptime(' '.join((date, time)), "%Y-%m-%d %H:%M:%S")

    def find(self, filters, start=None, end=None):
        try:
            frame = self.index.ix[slice(start, end)]
            bs = pd.DataFrame({key: frame[key] == value for key, value in filters.items()}).product(axis=1)
            return frame[bs==1].index
        except:
            return []

    def dates(self, start=None, end=None):
        return self.index.ix[slice(start, end)].index

    def check(self):
        count = 0
        for date in self.find({'tick': 0}):
            if os.path.exists(self.tick_path(date)):
                self.fill(date, "tick")
                count += 1
        logging.warning("%s | tick fulfilled | %s", self.code, count)
        return self.index

    def fill(self, idx, col):
        self.index.ix[idx, col] = 1

    def empty(self, idx, col):
        self.index.ix[idx, col] = 0

    def __getitem__(self, item):
        return pd.read_csv(self.tick_path(item), index_col="time")

    def __setitem__(self, key, value):
        if isinstance(value, pd.DataFrame):
            value.to_csv(self.tick_path(key))

    def __delitem__(self, key):
        os.remove(self.tick_path(key))


class RootManager(object):

    def __init__(self, root):
        self.root = root
        self._stocks = {}

    def check(self, codes):
        for code in codes:
            stock = self.get(code)
            try:
                stock.check()
                stock.flush()
            except Exception as e:
                logging.error("%s | check tick error | %s", code, e)

    def stock_dir(self, code):
        return os.path.join(self.root, code)

    def get(self, item):
        path = self.stock_dir(item)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        return StockDir(self.stock_dir(item), item)

    def delete(self, code, start=None, end=None):
        stock = self.get(code)
        return list(self._delete_tick(stock, start, end))

    def _delete_tick(self, stock, start=None, end=None):
        for date in stock.find({"tick": 1}, start, end):
            try:
                del stock[date]
            except Exception as e:
                logging.error("delete tick | %s | %s | %s", stock, date, e)
            else:
                yield date


    def __getitem__(self, item):
        if item in self._stocks:
            return self._stocks[item]
        else:
            stock = self.get(item)
            self._stocks[item] = stock
            return stock

    def __delitem__(self, key):
        del self._stocks[key]


NAME = "manager"


def conf_manager():
    if NAME in globals():
        return globals()[NAME]
    else:
        globals()[NAME] = RootManager(config.ROOT)
        return globals()[NAME]