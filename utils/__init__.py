from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import logging
import sys
import uuid

def __create_logger() -> logging.Logger:
    """
    Function for creating a logger to be used across the application.
    The logger will write to the console and to a file (1 file per day).

    Returns
    -------
        logging.Logger - the logger object
    """
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)

    fileName = f"./logs/{datetime.now().strftime('%Y-%m-%d')}.log"
    fileFormatter = logging.Formatter("[%(asctime)s] - [%(levelname)s] - [" + str(uuid.uuid4()) + "] - [%(module)s] - [%(funcName)s] - %(message)s")

    fileHandler = TimedRotatingFileHandler(fileName, when="d", interval=1,  backupCount=5)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(fileFormatter)
    logger.addHandler(fileHandler)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    logger.addHandler(streamHandler)

    def exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.exception("Uncaught Exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = exception_handler

    return logger

LOGGER: logging.Logger = __create_logger()
