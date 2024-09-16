import sys
import logging
import os


def setup_logging():
    logger = logging.getLogger()
    for h in logger.handlers:
        logger.removeHandler(h)

    h = logging.StreamHandler(sys.stdout)

    # use whatever format you want here
    FORMAT = '%(levelname)s %(message)s'
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)

    logging_level = "INFO"
    if "LOGGING_LEVEL" in os.environ:
        logging_level = os.environ["LOGGING_LEVEL"].upper()
    print("logging_level: "+logging_level)
    level = getattr(logging, logging_level)
    logger.setLevel(level)
    logger.setLevel(logging.INFO)

    return logger


logger = setup_logging()
