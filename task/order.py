from task.celery import app
from py12306.helpers.TicketHandler import TicketHandler
from py12306.helpers.cache_service import CacheService
from py12306.helpers.db_service import DbService
from task.logging_facory import getLogger
DICT_SEAT_MAP={
    'bussiness_seat':'商务座',
    'one_seat':'一等座',
    'two_seat':'二等座',
    'high_soft_sleeper':'高级软卧',
    'soft_sleeper':'软卧',
    'dong_sleeper':'动卧',
    'hard_sleeper':'硬卧',
    'soft_seat':'软座',
    'hard_seat':'硬座',
    'no_seat':'无座'
}
dbService=DbService()
cacheService=CacheService()
logger=getLogger(__name__)
@app.task
def order(userid,order_info):
    ticket_handler=TicketHandler.getTicketHandlerInstance(userid)
    ticket_handler.order(order_info,userid)
    return