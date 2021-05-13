from task.task_celery import app
from py12306.logging_factory import getLogger
logger=getLogger(__name__)

from wxpusher.ticket.send_ticket import send_message
MESSAGE_ORDER_SUCCESS_NOTIFICATION_TRAIN_INFO= '车次信息：{}  {} -> {},发车时间:{},乘车日期 {},席位:{},乘车人:{}'
MESSAGE_ORDER_SUCCESS_NOTIFICATION_CONTENT = '请及时登录12306账号[{}]，打开 \'未完成订单\'，在30分钟内完成支付!'
@app.task
def send_notification(order_info):
    # order_info['trainNum'] = qtr.left_station
    # order_info['left_date'] = datetime.datetime.strftime(waitUser.left_date, '%Y-%m-%d')
    # order_info['seat'] = order_seat
    # order_info['passengers'] = waitUser.passengers.split(",")
    # order_info['secret_str'] = qtr.secret_str
    # order_info['left_station'] = qtr.left_station
    # order_info['arrive_station'] = qtr.arrive_station
    # order_info['left_time'] = qtr.left_time
    #order_info['username'] = user.username
    train_str=MESSAGE_ORDER_SUCCESS_NOTIFICATION_TRAIN_INFO.format(order_info['trainNum'],order_info['left_station'],
                                                         order_info['arrive_station'], order_info['left_time'],
                                                         order_info['left_date'],order_info['seat'],order_info['passengers'] )
    order_str= MESSAGE_ORDER_SUCCESS_NOTIFICATION_CONTENT.format(order_info['username'])
    logger.info(train_str)
    logger.info(order_str)
    send_message(train_str)
    send_message(order_str)
