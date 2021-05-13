from task.celery import app
from py12306.helpers.request import Request
from py12306.logging_factory import getLogger
import requests
from py12306.helpers.cache_service import CacheService
import  json
cacheService=CacheService()
logger=getLogger(__name__)
@app.task
def get_cookies():
    api=Request()
    url='https://kyfw.12306.cn/'
    response=api.get(url)
    print(response.cookies)
    dict_cookie=requests.utils.dict_from_cookiejar(response.cookies)
    logger.info("reponse cookie %s",response.cookies)
    cacheService.save_cookie('Internal',dict_cookie)
if __name__ == '__main__':
    get_cookies()
    cacheService.get_cookie("Internal")