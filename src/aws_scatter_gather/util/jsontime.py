import datetime

import time

_JSON_TS_FORMATS = ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"]


def now_epoch_millis() -> int:
    return int(round(time.time() * 1000))


def now() -> str:
    return format(datetime.datetime.now())


def format(d: datetime.datetime) -> str:
    return d.strftime(_JSON_TS_FORMATS[0])


def parse(s) -> datetime.datetime:
    for f in _JSON_TS_FORMATS:
        try:
            return datetime.datetime.strptime(s, f)
        except ValueError:
            pass
    raise ValueError("Cannot parse '{}'.".format(s))
