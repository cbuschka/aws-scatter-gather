import datetime
import json as orig_json
from decimal import Decimal


class DecimalAndSetAwareJsonEncoder(orig_json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y%m%dT%H%M%S.%fZ")
        return orig_json.JSONEncoder.default(self, obj)


def loads(*kargs, **kwargs):
    return orig_json.loads(*kargs, **kwargs)


def load(*kargs, **kwargs):
    return orig_json.load(*kargs, **kwargs)


def dumps(*kargs, **kwargs):
    kwargs["cls"] = DecimalAndSetAwareJsonEncoder
    return orig_json.dumps(*kargs, **kwargs)


def dump(*kargs, **kwargs):
    kwargs["cls"] = DecimalAndSetAwareJsonEncoder
    return orig_json.dump(*kargs, **kwargs)
