FROM registry.docker-cn.com/library/python:3.6

ENV SINTA_ROOT="/data"
ADD . /sinta
WORKDIR /sinta

RUN apt-get update
RUN apt-get install -y cron
RUN crontab routing/timelist
RUN echo 'Asia/Shanghai' >/etc/timezone & cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "export SINTA_ROOT=/data; export WORKDIR=/sinta/sinta; export PYTHONPATH=/sinta" > /etc/profile.d/env.sh
# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple git+https://github.com/cheatm/sinta.git
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tushare --no-cache-dir

WORKDIR /sinta/sinta

VOLUME ["/data", "/logs"]

CMD /usr/sbin/cron -f