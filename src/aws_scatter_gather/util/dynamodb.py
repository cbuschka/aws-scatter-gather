from decimal import Decimal


def clean(o):
    if isinstance(o, dict):
        for k, v in o.items():
            o[k] = clean(v)
    elif isinstance(o, list):
        for index, v in enumerate(o):
            o[index] = clean(v)
    elif isinstance(o, Decimal):
        o = int(o)

    return o
