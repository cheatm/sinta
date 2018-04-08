#! /bin/bash

source /etc/profile

sinta index update
sinta require tick
sinta check tick
sinta write master
sinta check master
sinta write freq
sinta check freq
sinta table update -s `date "1 day ago" +\%Y-\%m-\%d`
