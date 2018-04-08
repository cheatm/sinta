# encoding:utf-8
import logging.config
import logging
import os


ROOT = os.environ.get("SINTA_ROOT", "/data")
MONGODB_URL = "mongodb://localhost:27017"
MIN1 = 'Stock_1M'
H = "Stock_H"
D = "Stock_D"
FREQ = ["H", "D"]

LOG_COL = "log.sinta"
LOG_DIR = None
LEVEL = logging.WARNING


KEYS = ("ROOT", "MONGODB_URL", "MIN1", "H", "D", "FREQ", "LOG_DIR", "LEVEL")


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

    init_log()


FORMAT = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
LOG_CONF_FILE = "log.conf"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def init_log():

    log_conf_path = os.path.join(ROOT, LOG_CONF_FILE)
    if os.path.isfile(log_conf_path):
        logging.config.fileConfig(log_conf_path)
    else:
        if LOG_DIR is not None:
            from datetime import date

            file_name = os.path.join(LOG_DIR, "sinta_log.%s" % date.today())
            logging.basicConfig(
                handlers=[logging.StreamHandler(), logging.FileHandler(file_name, encoding='utf-8')],
                datefmt=DATEFMT,
                format=FORMAT,
                level=LEVEL
            )
        else:
            logging.basicConfig(
                datefmt=DATEFMT,
                format=FORMAT,
                level=LEVEL
            )