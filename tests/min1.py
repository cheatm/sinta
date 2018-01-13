import tushare
import requests
import json


# response = requests.get("http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sz000001,day,,,640,qfq&r=0.36427983230079874")
# print(response.content)
print(tushare.get_k_data("000001", start="2016-01-01", autype=None))