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
class TicketArrPipeline:
    def process_item(self, item, spider):
        order_info={}
        str_arr = item['arr']
        logger.info("TicketArrPipeline")
        for str_tmp in str_arr:
            qtr = handle_response_query_date(str_tmp)
            left_date = datetime.datetime.strptime(qtr.left_date,'%Y%m%d').strftime('%Y-%m-%d')
            arr_seat = handle_seat(qtr)
            if arr_seat:
                #取第一个
                #print(" {}  {} ".format(item['num'],item['no']))
                for seat in arr_seat:
                    order_seat=seat
                    waitUser=db_service.get_wait_user_scrapy(qtr.num,order_seat,qtr.left_station,qtr.arrive_station,left_date)
                    if waitUser:
                        logger.info("Search condition %s %s %s %s %s ",qtr.num,order_seat,qtr.left_station,qtr.arrive_station,left_date)
                        logger.info("Wait user %s", waitUser)
                        order_info['trainNum']=qtr.left_station
                        order_info['left_date']=datetime.datetime.strftime(waitUser.left_date,'%Y-%m-%d')
                        order_info['seat']=order_seat
                        order_info['passengers']=waitUser.passengers.split(",")
                        order_info['secret_str']=qtr.secret_str
                        order_info['left_station']=qtr.left_station
                        order_info['arrive_station']=qtr.arrive_station
                        order_info['left_time']=qtr.left_time
                        #yield 不会阻塞其他，待测
                        yield order(order_info,waitUser)
        return {}
def order(order_info,wait_user):
    userid=wait_user.account_key
    id=wait_user.id
    logger.info("Start order %s  %s", order_info, userid)
    handler = TicketHandler.getTicketHandlerInstance(userid)
    #乐观锁，锁住
    db_service.change_waituser(id,WaitUserState.ORDERING.value)
    order_result=handler.order(order_info, userid)
    if order_result:
       db_service.update_waituser_result(id,WaitUserState.END.value,True,"SUCCESS")
       #异步发送通知，一般短信接口都限ip
       user=db_service.getAccount(userid)
       order_info['username']=user.username
       send_notification.delay(order_info)
    else:
       #重置锁
       db_service.change_waituser(id,WaitUserState.RUNNING.value)
    logger.info("End order")
class TicketResultPipeline:
    def process_item(self, item, spider):
        logger.info("Result pipeline")
        logger.info(item['info'])
        qtr = handle_response_query_date(item['info'])
        arr_seat=handle_seat(qtr)
        logger.info("Arr seat %s",arr_seat)
        if arr_seat:
            print()
            # yield OrderTicketItem(secret_str=qtr.secret_str,no=qtr.no,num=qtr.num,valid_seat=arr_seat,
            #                       left_station=qtr.left_station,arrive_station=qtr.arrive_station,
            #                       left_time=qtr.left_time,left_date=qtr.left_date)
class OrderTicketPipeline:
    def process_item(self, item, spider):
        order_info={}
        str_arr = item['arr']
        for str_tmp in str_arr:
            qtr = handle_response_query_date(str_tmp)
            arr_seat = handle_seat(qtr)
            logger.info("Arr seat %s", arr_seat)
            if arr_seat:
                #取第一个
                #print(" {}  {} ".format(item['num'],item['no']))
                logger.info("OrderTicketPipeline")
                order_seat=arr_seat[0]
                waitUser=db_service.get_wait_user_scrapy(qtr.num,order_seat,qtr.left_station,qtr.arrive_station,qtr.left_date)
                logger.info("Wait user %s",waitUser)
                if waitUser:
                    handler=TicketHandler.getTicketHandlerInstance(waitUser.account_key)
                    order_info['trainNum']=qtr.left_station
                    order_info['left_date']=waitUser.left_date
                    order_info['seat']=order_seat
                    order_info['passengers']=waitUser.passengers
                    order_info['secret_str']=qtr.secret_str
                    order_info['left_station']=qtr.left_station
                    order_info['arrive_station']=qtr.arrive_station
                    order_info['left_time']=qtr.left_time
                    logger.info("Start order " )
                    handler.order(order_info,waitUser.account_key)
                    logger.info("End order")
        return {}
# class SuccessOrderPipeline:
#     def process_item(self, item, spider):
#         success_order_info={}
#         #取第一个
#         print(" {}  {} ".format(item['num'],item['no']))
#         seat=item['valid_seat']
#         order_seat=seat[0]
#         waitUser=db_service.get_wait_user_scrapy(item['num'],order_seat,item['left_station'],item['arrive_station'])
#         if waitUser:
#             handler=TicketHandler.getTicketHandlerInstance(waitUser.account_key)
#             success_order_info['trainNum']=item['num']
#             success_order_info['left_date']=waitUser.left_date
#             success_order_info['seat']=seat
#             success_order_info['passengers']=waitUser.passengers
#             success_order_info['secret_str']=item['secret_str']
#             success_order_info['left_station']=item['left_station']
#             success_order_info['arrive_station']=item['arrive_station']
#             success_order_info['left_time']=item['left_time']
#             handler.order(success_order_info,waitUser.account_key)
#         return item
if __name__ == '__main__':
    order_info={'trainNum': '合肥', 'left_date': datetime.date(2020, 6, 8), 'seat': '二等座', 'passengers': '丁为庆',
     'secret_str': 'fIrqnhSqEFY7ZAGqQkmcLYEygxCpfnyqjfjdfxfIwgnmN9dtaBM%2FGoJ7helUSyYOh%2F7OfN4G4W%2Fe%0A6v18A4LwwZja3KgDARIME1mZRdkRECYdJwXq5%2B6ugx9SjwAh1pgpG%2FwLNMUeR7fT3kCbruSLmncj%0AtowL6OvRUeq73Gqyghr34lGYOWJp5QreeDcrwq%2BmeMn%2ByjrAu30CvPKEugde4NFwocZBed31HhPG%0AHamiFN3VyLc3Ztj423aIDEOhEOs11fOx8KwhtrATd6DmTbs5mCMpqSC%2B0VyboadR1a4RXp8%3D',
     'left_station': '合肥', 'arrive_station': '苏州', 'left_time': '17:10'}

    handler=TicketHandler.getTicketHandlerInstance('f2298ccd-bcc5-4130-a770-8ca218e17824')
    handler.order(order_info,'f2298ccd-bcc5-4130-a770-8ca218e17824')