# encoding:utf-8
import pandas as pd
from datetime import datetime, time, timedelta
from itertools import chain


_0931_ = time(9, 31)
_1030_ = time(10, 30)
_1130_ = time(11, 30)
_1301_ = time(13, 1)
_1400_ = time(14)
_1500_ = time(15)


PRICE_MAP = {
    "close": "last",
    "open": "first",
    "high": "max",
    "low": "min"
}


VT = ["volume", "turnover"]
COLUMNS = ['close', "open", "high", "low", "volume", "turnover"]


RESAMPLE_MAP = {
    "close": "last",
    "open": "first",
    "high": "max",
    "low": "min",
    "volume": "sum",
    "turnover": "sum"
}


def timer(dt):
    t = dt.time()

    if t < _0931_:
        return dt.replace(hour=_0931_.hour, minute=_0931_.minute, second=0)
    elif t <= _1130_:
        return dt + timedelta(seconds=(60-t.second)%60)
    elif t < _1301_:
        return dt.replace(hour=_1301_.hour, minute=_1301_.minute, second=0)
    elif t <= _1500_:
        return dt + timedelta(seconds=(60-t.second)%60)
    else:
        return dt.replace(hour=_1500_.hour, minute=_1500_.minute, second=0)


def tick2min1(frame, date):
    if isinstance(frame, pd.DataFrame):
        data = frame.rename_axis(timer)
        grouper = data.groupby(data.index)
        result = grouper["price"].agg(PRICE_MAP)
        result["volume"] = grouper["volume"].agg(sum)
        result["turnover"] = grouper["amount"].agg(sum)
        index = date2index(date)
        result = pd.DataFrame(result, index, COLUMNS)
        result[VT] = result[VT].fillna(0)
        result["close"].ffill(inplace=True)
        result["open"].bfill(inplace=True)
        return result.ffill(1).bfill(1)


def date2index(date):
    date = datetime.strptime(date, "%Y-%m-%d")

    return pd.Index(
        list(chain(
            pd.DatetimeIndex(freq='1min', start=date.replace(hour=9, minute=31), end=date.replace(hour=11, minute=30)),
            pd.DatetimeIndex(freq='1min', start=date.replace(hour=13, minute=1), end=date.replace(hour=15, minute=0))
        ))
    )


def min2hour(frame):
    return frame.groupby(frame.index.map(time_hour)).agg(RESAMPLE_MAP)


def time_hour(dt):
    t = dt.time()
    d = dt.date()
    if t <= _1030_:
        return datetime.combine(d, _1030_)
    elif t <= _1130_:
        return datetime.combine(d, _1130_)
    elif t <= _1400_:
        return datetime.combine(d, _1400_)
    else:
        return datetime.combine(d, _1500_)


def min2day(frame):
    return frame.groupby(frame.index.map(lambda t: t.replace(hour=15, minute=0))).agg(RESAMPLE_MAP)