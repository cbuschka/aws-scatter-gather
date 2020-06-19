import logging

logger = logging.getLogger()


def configure(name):
    logging.basicConfig(level=logging.INFO, format='{} [%(levelname)s] %(message)s'.format(name))
    global logger
    logging.getLogger(name)
    logger.setLevel(logging.INFO)


def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)


def info(*args, **kwargs):
    logger.info(*args, **kwargs)


def warning(*args, **kwargs):
    logger.warning(*args, **kwargs)


def error(*args, **kwargs):
    logger.error(*args, **kwargs)
