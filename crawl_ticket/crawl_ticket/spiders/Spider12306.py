import scrapy
from py12306.helpers.cache_service import CacheService
import time
import json
import logging
from crawl_ticket.items import TicketArrItem
from scrapy_redis.spiders import RedisSpider
from scrapy.http.response.text import TextResponse
from scrapy.http.response.html import HtmlResponse
class Spider12306(scrapy.Spider):
    name = "Spider12306"
    cacheService=CacheService()

    def start_requests(self):
        urls = [
            'https://www.baidu.com'
        ]
        #cookies=self.cacheService.get_cookie('Internal')
        #print(cookies)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    #单个爬虫可以处理很多并发
    def parse(self, response):
        #记得处理cookie 过期
        #出异常会终止
        #self.log("Response %s", response.body)
        # filename = '12306_response.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        if isinstance(response,TextResponse):
            if not "<" in response.text:
                ticket_arr=json.loads(response.text)['data']['result']
                if ticket_arr:
                    yield TicketArrItem(arr=ticket_arr)
                #yield 1
        # parse 返回另外一个车次的url，这样队列中很少
        url = response.url
       # cookies = self.cacheService.get_cookie('Internal')
       # time.sleep(10)
        yield scrapy.Request(url=url,callback=self.parse)
    @staticmethod
    def close(spider, reason):
        return super().close(spider, reason)
