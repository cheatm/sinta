import tushare
import requests
import pandas as pd
import logging
import re


HIS_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "keep-alive",
    "Referer": "http://finance.sina.com.cn/data/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36}"
}


TICK_HISTORY = "http://market.finance.sina.com.cn/downxls.php?"
HISTORY_TICK_COLUMNS = ['time', 'price', 'change', 'volume', 'amount', 'trend']
HISTORY_FORMAT = "\n%s" % "\t".join(['(.*?)']*6)
FLOAT_TYPE = ['price', 'volume', 'amount']
REJECTION = "拒绝访问".encode('utf-8')
NODATA = "当天没有数据".encode("gbk")


class SinaBreak(Exception):

    def __init__(self):
        self.message = "SinaBreak"

    def __str__(self):
        return "SinaBreakException"


class SinaNoData(Exception):

    def __init__(self):
        self.message = "SinaNoData"

    def __str__(self):
        return "SinaNoDataException"


def reconnect_wrap(retry=3, wait=0.1, error=ConnectionError):
    def wrapper(func):
        def reconnect(*args, **kwargs):
            rt = retry
            while rt >= 0:
                try:
                    return func(*args, **kwargs)
                except error as e:
                    logging.error("%s | %s", func, e)
                    rt -= 1
            raise e

        return reconnect
    return wrapper


def join_params(**kwargs):
    return '&'.join(['%s=%s' % item for item in kwargs.items()])


def make_url(*args):
    return ''.join(args)


# 获取历史tick数据(str)
def history_text(code, date_, **kwargs):
    url = make_url(TICK_HISTORY, join_params(symbol=code, date=date_))
    return requests.get(url, headers=HIS_HEADERS, timeout=10, **kwargs).content


def check_response(content):
    if REJECTION in content:
        raise SinaBreak()
    elif NODATA in content:
        raise SinaNoData()
    else:
        return content


def text2tick(content):
    tick = pd.DataFrame(re.findall(HISTORY_FORMAT, content.decode('gbk'), re.S), columns=HISTORY_TICK_COLUMNS)
    tick[FLOAT_TYPE] = tick[FLOAT_TYPE].applymap(float)
    tick['volume'] *= 100
    return tick.set_index("time")[FLOAT_TYPE]


# 获取历史tick数据(DataFrame)
@reconnect_wrap()
def history_tick(code, date_, **kwargs):
    text = history_text(code, date_, **kwargs)
    text = check_response(text)
    return text2tick(text)


def daily(code, start="", end=""):
    data = tushare.get_k_data(code, start, end, autype=None).set_index("date")
    data.pop("code")
    data["volume"] *= 100
    return data


from datetime import datetime


def daily_index(code, start="", end=""):
    data = tushare.get_k_data(code, start, end, index=True).set_index("date")
    data.pop("code")
    data["volume"] *= 100
    return data.rename(lambda t: datetime.strptime(t, "%Y-%m-%d").replace(hour=15))
