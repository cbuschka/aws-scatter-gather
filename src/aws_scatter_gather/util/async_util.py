import asyncio


def async_to_sync(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(f(*args, **kwargs))
        return result

    return wrapper
