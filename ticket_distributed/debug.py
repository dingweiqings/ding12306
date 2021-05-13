from scrapy.cmdline import execute
from scrapy import Request
if __name__ == '__main__':
    #逗号变成空格分隔
    execute(['scrapy', 'crawl', 'ticket','-a','master=True'])
    # from py12306.helpers.cache_service import CacheService
    # cacheService=CacheService()
    # cookies= cacheService.get_cookie()
    # session.cookies=requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
    # url='https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2020-06-13&leftTicketDTO.from_station=SZH&leftTicketDTO.to_station=ENH&purpose_codes=ADULT'
    # response=session.get(url)
    #
    # print(response.status_code)