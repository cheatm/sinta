from sinta import config, codes
from sinta.operates.db import DBManager
from sinta.operates.files import IndexManager
import click


config.init()
codes.init()


CODE = click.argument('code', required=False, nargs=-1)
START = click.option('-s', '--start', default=None, type=click.STRING)
END = click.option('-e', '--end', default=None, type=click.STRING)
COVER = click.option("-c", "--cover", is_flag=True, default=True)
HOW = click.option("-h", "--how", default="insert", type=click.STRING)
FREQ = click.option("-f", "--freq", default=",".join(config.FREQ), type=click.STRING)


def DEFAULT_CODE(func):
    wrapped_func = CODE(func)

    def wrapped(**kwargs):
        code = kwargs.get("code", [])
        if len(code) == 0:
            kwargs["code"] = codes.STOCKS
        return wrapped_func(**kwargs)

    wrapped.__name__ = func.__name__
    return wrapped


check = click.Group("check")


@check.command(name="master")
@START
@END
@COVER
@DEFAULT_CODE
def check_master(code, start, end, cover=False):
    manager = DBManager.conf()
    manager.check_master(code, start, end)


@check.command(name="freq")
@START
@END
@COVER
@FREQ
@DEFAULT_CODE
def check_freq(code, freq, start, end, cover=False):
    freq = freq.split(",")
    manager = DBManager.conf()
    manager.check_freq(freq, code, start, end, cover)


@check.command(name="tick")
@DEFAULT_CODE
def check_tick(code):
    manager = IndexManager.conf()
    manager.rm.check(code)


write = click.Group("write")


@write.command(name="master")
@START
@END
@COVER
@DEFAULT_CODE
def write_master(code, start, end, how, cover=False):
    manager = DBManager.conf()
    manager.write_master(code, start, end, how, cover)


@write.command(name="freq")
@START
@END
@COVER
@FREQ
@HOW
@DEFAULT_CODE
def writer_freq(code, freq, start, end, how, cover=False):
    manager = DBManager.conf()
    manager.write_freqs(freq, code, start, end, how, cover)


require = click.Group("require")


@require.command()
@START
@END
@DEFAULT_CODE
def tick(code, start, end):
    manager = IndexManager.conf()
    manager.require_range(code, start, end)


index = click.Group("index")


@index.command(name="create")
@START
@END
@DEFAULT_CODE
def create(code, start, end):
    manager = IndexManager.conf()
    manager.create_indexes(code, start, end)


group = click.Group(
    commands={"write": write,
              "check": check,
              "require": require,
              "index": index}
)


if __name__ == '__main__':
    # import sys
    # sys.argv.extend("write".split(" "))
    group()
