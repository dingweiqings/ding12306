import logging
import datetime
import os
from py12306.logging_config import PRODUCTION
if PRODUCTION:
    log_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s  %(message)s')
    debug_list = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR,'CRITICAL': logging.CRITICAL}
    # create logger
    log_name = 'ding.log'
    logfile = log_path + os.sep + log_name
    logging.basicConfig(level=debug_list['DEBUG'],format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',filename=logfile,filemode='a')
console=''
if not PRODUCTION:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    console.setFormatter(formatter)
def getLogger(name):
    logger=logging.getLogger(name)
    if not PRODUCTION:
        logger.addHandler(console)
    return logger
