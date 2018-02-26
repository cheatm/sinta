from sinta import config, codes
from sinta.operates.db import DBManager
from sinta.operates.files import IndexManager
import click


config.init()
codes.init()


CODE = click.argument('code', required=False, nargs=-1)
START = click.option('-s', '--start', default=None, type=click.STRING)
END = click.option('-e', '--end', default=None, type=click.STRING)
COVER = click.option("-c", "--cover", is_flag=True, default=False)
HOW = click.option("-h", "--how", default="insert", type=click.STRING)
FREQ = click.option("-f", "--freq", default=",".join(config.FREQ), type=click.STRING)


def DEFAULT_CODE(func):

    def wrapped(**kwargs):
        code = kwargs.get("code", [])
        if len(code) == 0:
            kwargs["code"] = codes.STOCKS
        return func(**kwargs)

    wrapped.__name__ = func.__name__
    return CODE(wrapped)


check = click.Group("check")


@check.command(name="master")
@START
@END
@COVER
@DEFAULT_CODE
def check_master(code, start, end, cover=False):
    manager = DBManager.conf()
    manager.check_master(code, start, end, cover)


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
@HOW
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


@write.command(name="idx")
@START
@END
@CODE
def write_idx(code, start, end):
    if len(code) == 0:
        code = codes.INDEXES
    manager = DBManager.conf()
    manager.save_indexes(code, start, end)



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
@click.option('-s', '--start', default="", type=click.STRING)
@click.option('-e', '--end', default="", type=click.STRING)
@COVER
@DEFAULT_CODE
def create(code, start, end, cover=False):
    manager = IndexManager.conf()
    manager.create_indexes(code, start if start else "", end if end else "", cover)


@index.command(name="delete")
@START
@END
@DEFAULT_CODE
def delete(code, start, end):
    manager = IndexManager.conf()
    manager.delete(code, start, end)


@index.command(name="update")
@START
@END
@DEFAULT_CODE
def update(code, start, end):
    manager = IndexManager.conf()
    manager.update_indexes(code, start if start else "", end if end else "")


group = click.Group(
    commands={"write": write,
              "check": check,
              "require": require,
              "index": index}
)


@group.command()
def conf():
    text = "\n".join(["{} = {}".format(key, getattr(config, key)) for key in config.KEYS])
    click.echo(text)


if __name__ == '__main__':
    group()
