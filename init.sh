#! /bin/bash

if [ -n "$CREATE_OPTION" ]
then
    sinta index create $CREATE_OPTION
else
    sinta index create
fi

if [ -n "$PRE_CHECK" ]
then
    sinta check tick
    sinta check master
    sinta check freq
fi

if [ -n "$SYNC_TABLE" ]
then
    sinta table $SYNC_TABLE
fi

/usr/sbin/cron -f