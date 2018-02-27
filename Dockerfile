FROM registry.docker-cn.com/library/python:3.6

RUN apt-get update
RUN apt-get install -y cron
RUN echo 'Asia/Shanghai' >/etc/timezone & cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ADD . /sinta
WORKDIR /sinta

ENV SINTA_ROOT="/data" LC_ALL="C.UTF-8" LANG="C.UTF-8"
RUN ln -s routing/env.sh /etc/profile.d/env.sh

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tushare --no-cache-dir
RUN python setup.py install

RUN crontab routing/timelist

VOLUME ["/data", "/logs"]

CMD /usr/sbin/cron -f