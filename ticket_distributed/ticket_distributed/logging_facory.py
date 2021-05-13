import logging
import os
import sys
from task.loggin_config import PROFILE
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
def getLogger(name):
    logger=logging.getLogger(name)
    if PROFILE == 'PRODUCTION':
        logger.setLevel(level=logging.INFO)
        file = logging.FileHandler("ding.log")
        file.setLevel(logging.INFO)
        file.setFormatter(formatter)
        logger.addHandler(file)
    if PROFILE == 'DEV':
        logger.setLevel(level=logging.INFO)
        #默认是stderr,两种都是控制台，但是err是红色的
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        logger.addHandler(console)
    return logger
