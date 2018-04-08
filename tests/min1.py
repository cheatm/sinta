import os
import pandas as pd
from itertools import chain
# from datetime import time, timedelta

ROOT = "X:\\Users\\caimeng\\Desktop\\cp"
MIN1 = os.path.join(ROOT, "000001.sz.csv")
TICK = os.path.join(ROOT, "sz000001.csv")

RANGE = list(chain(range(1, 121), range(122, 242)))


def get_local():
    min1 = pd.read_csv(MIN1, header=None, names=["open", "high", "low", "close", "volume", "turnover", "other"])
    min1.loc[130100000, ["volume", "turnover"]] += min1.loc[130000000, ["volume", "turnover"]]
    min1.loc[93100000, ["volume", "turnover"]] += min1.loc[93000000, ["volume", "turnover"]]
    return min1.iloc[RANGE]


def get_sina():
    tick = pd.read_csv(TICK, index_col="time")
    return


def time_end(hour, minute, second):
    if second == 0:
        return hour * 10000000 + minute * 100000
    else:
        if minute < 59:
            return hour * 10000000 + (minute+1) * 100000
        else:
            return (hour+1) * 10000000


def grouper(string):
    h, m, s = string.split(':')
    return time_end(int(h), int(m), int(s))


if __name__ == '__main__':
    # print(get_local())
    print(grouper("14:57:00"))