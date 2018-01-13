# encoding:utf-8
import os


ROOT = os.environ.get("SINTA_ROOT", "/data")
MONGODB_URL = "mongodb://localhost:27017"
MIN1 = 'stock_1min'
H = "Stock_H"
D = "Stock_D"

FREQ = ["H", "D"]


def update(dct):
    globals().update(dct)


def init_json(path):
    import json

    with open(path) as f:
        update(json.load(f))


def init():
    config_file = os.path.join(ROOT, 'config.json')
    if os.path.isfile(config_file):
        init_json(config_file)
