FROM registry.docker-cn.com/library/python:3.6

RUN apt-get update & apt-get install cron

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple git+https://github.com/cheatm/sinta.git
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tushare
RUN echo 'Asia/Shanghai' >/etc/timezone & cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime


