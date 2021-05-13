import json
import logging
import sys
sys.path.append("..")
from ticket_distributed.items import TicketArrItem
from scrapy_redis.spiders import RedisSpider
from scrapy.http.response.text import TextResponse
from ticket_distributed.redis_client import RedisClient
from py12306.helpers.TicketHandler import TicketHandler
import urllib.parse
import datetime
from py12306.config import Config
from scrapy_redis.utils import bytes_to_str
from scrapy import Request
from py12306.helpers.cache_service import CacheService
from py12306.helpers.db_service import DbService
import pickle
import requests
logger = logging.getLogger(__name__)
db_service=DbService()
class Spider12306(RedisSpider):
    name = 'ticket'
    redis_key = 'spider12306:start_urls'
    redis_parse_key='spider12306:parse_urls'
    redis_client=''
    master=False
    slave=False
    cacheService=CacheService()
    def __init__(self, *args, **kwargs):
        self.redis_client=RedisClient()
        if kwargs.get('master'):
           self.redis_key = 'spider12306:start_urls'
           self.redis_client.init_job(self.redis_key)
           self.master=True
        if kwargs.get('slave'):
           self.redis_key = 'spider12306:parse_urls'
           self.salve=True
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(Spider12306, self).__init__(*args, **kwargs)

    #单个爬虫可以处理很多并发
    def parse(self, response):
        #记得处理cookie 过期
        #出异常会终止
        #self.log("Response %s", response.body)
        # filename = '12306_response.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        if response.status==302:
            print(response)
        url=response.url
        valid_result,msg=self.judge_dage_ilegal(url)
        if not valid_result:
            self.log("Url should be terminate %s, msg %s" %(url,msg))
            return
        if 'error' in url:
          #  self.redis_client.lpush(self.redis_parse_key, url)
            return
        self.redis_client.lpush(self.redis_parse_key,url)
        if isinstance(response,TextResponse):
            #logger.info("Text %s",response.text)
            if response.text and not  "<" in response.text:
                ticket_arr = json.loads(response.text)['data']['result']
                if ticket_arr:
                    yield TicketArrItem(arr=ticket_arr)
                # yield 1
        #跑一次终止，定时任务读取放入redis
        # parse 返回另外一个车次的url，这样队列中很少
        # cookies = self.cacheService.get_cookie('Internal')
        # time.sleep(10)


    @staticmethod
    def close(spider, reason):
        return super().close(spider, reason)

    # def make_request_from_data(self, data):
    #     url = bytes_to_str(data, self.redis_encoding)
    #     cookies={}
    #     return Request(url=url,cookies=cookies)
    def judge_dage_ilegal(self,url):
        if 'error' in url:
          #  self.redis_client.lpush(self.redis_parse_key, url)
            return False,"Network error"
        result = urllib.parse.urlsplit(url)
        query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
        date_now = datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        date_query = datetime.datetime.strptime(str(query['leftTicketDTO.train_date']), "%Y-%m-%d")
        diff = (date_query-date_now).days
        if diff < 0:
           return False,'Left date error ,before now!'
        elif diff > Config.MAX_BUY_TIME:
            return False,'Left date error ,out of month'
        return True,"SUCCESS"
