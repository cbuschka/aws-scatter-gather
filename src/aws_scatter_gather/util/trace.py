import time

import aws_scatter_gather.util.logger as logger


def trace(message, *args):
    return Trace(message, *args)


def traced(f):
    def wrapper(*args, **kwargs):
        with trace("{} args={}, kwargs={}", f.__name__, [*args], {**kwargs}):
            return f(*args, **kwargs)

    return wrapper


class Trace(object):
    def __init__(self, message, *args):
        self.message = message.format(*args)

    def __enter__(self):
        self.start = time.time_ns()
        logger.info("START \"%s\"...", str(self.message))
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.end = time.time_ns()
        self.duration_milis = int((self.end - self.start) / 1000 / 1000)
        if exc_type is None:
            logger.info("SUCCESS of \"%s\". Duration %d millis.", str(self.message), self.duration_milis)
        else:
            logger.info("FAILURE of \"%s\". Duration %d millis.", str(self.message), self.duration_milis,
                        exc_info=True)

    async def __aenter__(self):
        self.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        self.__exit__(exc_type, exc_value, tb)
