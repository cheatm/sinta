# encoding:utf-8


STOCKS = ["000001", "000002"]
INDEXES = []


def update(dct):
    globals().update(dct)


def init_json(path):
    import json

    with open(path) as f:
        update(json.load(f))


def init():
    from sinta.config import ROOT
    import os

    code_file = os.path.join(ROOT, "codes.json")
    if os.path.isfile(code_file):
        init_json(code_file)