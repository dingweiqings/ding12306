import logging
import os
from web.logging_config import PROFILE

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
def getLogger(name):
    logger=logging.getLogger(name)
    if PROFILE == 'PRODUCTION':
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("ding.log")
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if PROFILE == 'DEV':
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logger.addHandler(console)
