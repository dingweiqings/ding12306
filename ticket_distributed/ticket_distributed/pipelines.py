# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from py12306.helpers.db_service import DbService
from py12306.helpers.TicketHandler import TicketHandler
#from .items import OrderTicketItem,TicketArrItem,TicketInfoItem
from py12306.helpers.QueryTrainConfig import *
from task.grabbing import handle_seat
from py12306.dto.QueryJob import WaitUserState
import logging
logger = logging.getLogger(__name__)
db_service=DbService()
from task.notification import send_notification
from task.grabbing import order
class TicketArrPipeline:
    def process_item(self, item, spider):
        order_info={}
        str_arr = item['arr']
        try:
            for str_tmp in str_arr:
                qtr = handle_response_query_date(str_tmp)
                if '-' != qtr.left_date:
                    left_date = datetime.datetime.strptime(qtr.left_date,'%Y%m%d').strftime('%Y-%m-%d')
                    arr_seat = handle_seat(qtr)
                    if arr_seat:
                        logger.info("Has seat %s",arr_seat)
                        #取第一个
                        #print(" {}  {} ".format(item['num'],item['no']))
                        for seat in arr_seat:
                            order_seat=seat
                            waitUser=db_service.get_wait_user_scrapy(qtr.num,order_seat,qtr.left_station,qtr.arrive_station,left_date)
                            if waitUser:
                                logger.info("Search condition %s %s %s %s %s ",qtr.num,order_seat,qtr.left_station,qtr.arrive_station,left_date)
                                logger.info("Wait user %s", waitUser)
                                order_info['trainNum']=qtr.num
                                order_info['left_date']=datetime.datetime.strftime(waitUser.left_date,'%Y-%m-%d')
                                order_info['seat']=order_seat
                                order_info['passengers']=waitUser.passengers.split(",")
                                order_info['secret_str']=qtr.secret_str
                                order_info['left_station']=qtr.left_station
                                order_info['arrive_station']=qtr.arrive_station
                                order_info['left_time']=qtr.left_time
                                #yield 不会阻塞其他，待测
                                order.delay(order_info,waitUser)
        except Exception as e:
            print("Occur error %s" ,e)

