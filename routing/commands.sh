#! /bin/bash

source /etc/profile

# python $WORKDIR/entry_point.py index update
python $WORKDIR/entry_point.py require tick
python $WORKDIR/entry_point.py check tick
python $WORKDIR/entry_point.py write master
python $WORKDIR/entry_point.py check master
python $WORKDIR/entry_point.py write freq
python $WORKDIR/entry_point.py check freq
