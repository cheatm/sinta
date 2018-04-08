FROM registry.docker-cn.com/library/python:3.6

RUN apt-get update
RUN apt-get install -y cron
RUN echo 'Asia/Shanghai' >/etc/timezone & cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ENV SINTA_ROOT="/data" LC_ALL="C.UTF-8" LANG="C.UTF-8"
ADD ./requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tushare --no-cache-dir

ADD . /sinta
WORKDIR /sinta

RUN ln -s /sinta/routing/env.sh /etc/profile.d/env.sh
RUN python setup.py install

RUN crontab routing/timelist

VOLUME ["/data", "/logs"]

CMD ["/bin/bash", "init.sh"]