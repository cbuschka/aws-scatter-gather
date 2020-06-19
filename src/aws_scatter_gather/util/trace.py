import time

import aws_scatter_gather.util.logger as logger


def trace(message, *args):
    return Trace(message, *args)


class Trace(object):
    def __init__(self, message, *args):
        self.message = message.format(*args)

    def __enter__(self):
        self.start = time.time_ns()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.end = time.time_ns()
        self.duration_milis = int((self.end - self.start) / 1000 / 1000)
        if exc_type is None:
            logger.info("\"%s\" SUCCESS. Duration %d millis.", str(self.message), self.duration_milis)
        else:
            logger.info("\"%s\" FAILED. Duration %d millis.", str(self.message), self.duration_milis,
                        exc_info=True)
