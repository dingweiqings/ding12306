# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
class TicketArrItem(scrapy.Item):
      arr=scrapy.Field()


class TicketInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    info=scrapy.Field()
    # secret_str = scrapy.Field()
    # no = scrapy.Field()
    # num = scrapy.Field()
    # seat_types = ''
    # from_station_no = 0
    # to_station_no = 0
    # left_station = ''
    # arrive_station = ''
    # left_date = ''
    # left_time = ''
    # arrive_time = ''
    # time = 0
    # arrive_at_current_day = 'N'
    # bussiness_seat = ''
    # one_seat = ''
    # two_seat = ''
    # high_soft_sleeper = ''
    # soft_sleeper = ''
    # dong_sleeper = ''
    # hard_sleeper = ''
    # soft_seat = ''
    # hard_seat = ''
    # no_seat = ''
    # other = ''
    # ops = ''
class OrderTicketItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    secret_str = scrapy.Field()
    no = scrapy.Field()
    num = scrapy.Field()
    valid_seat=scrapy.Field()
    # seat_types = ''
    # from_station_no = 9
    # to_station_no = 0
    left_station = scrapy.Field()
    arrive_station = scrapy.Field()
    left_date=scrapy.Field()
    # left_date = ''
    # left_time = ''
    # arrive_time = ''
    # time = 0
    # arrive_at_current_day = 'N'
    # bussiness_seat = ''
    # one_seat = ''
    # two_seat = ''
    # high_soft_sleeper = ''
    # soft_sleeper = ''
    # dong_sleeper = ''
    # hard_sleeper = ''
    # soft_seat = ''
    # hard_seat = ''
    # no_seat = ''
    # other = ''
    # ops = ''
# class SuccessOrderItem(scrapy.Item):
#       account_key=scrapy.Field()
#       train_num=scrapy.Field()
#       left_station=scrapy.Field()
#       arrive_station = scrapy.Field()
#       left_time=scrapy.Field()
#       seat=scrapy.Field()
if __name__ == '__main__':
    print(TicketArrItem(info='123'))