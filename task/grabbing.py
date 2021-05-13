from py12306.dto.QueryJob import QueryJobGrabbing,QueryJobState
import datetime
from py12306.helpers.TicketHandler import TicketHandler
import time
from py12306.exceptions.BussinessException import BussinessException
from py12306.helpers.QueryTrainConfig import judge_date_legal
from task.task_celery import app
from py12306.helpers.TicketHandler import TicketHandler
from py12306.helpers.cache_service import CacheService
from py12306.helpers.db_service import DbService
from task.order import order
from py12306.helpers.QueryTrainConfig import *
from task.logging_facory import getLogger
from task.notification import send_notification
from py12306.dto.QueryJob import WaitUserState
from py12306.helpers.api import LEFT_TICKETS

RETRY=3
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
sleep_time = 10

def grabbing(job):
        if job.state == QueryJobState.NEW.value:
            logger.info("Job is new")
        elif job.state == QueryJobState.START.value:
            #job 是对象，可以直接修改，不是int str 这种不可变对象
            job.state=QueryJobState.RUNNING.value
            logger.info("Change job state to running")
            grabbing(job)
           #修改值为running
        elif job.state == QueryJobState.RUNNING.value:
            doRunning(job)
            logger.info("Job running")
        elif job.state == QueryJobState.BLOCK.value:
            logger.info("Job block")
        elif job.state == QueryJobState.END.value:
            logger.info("Job is already end,do nothing")

def get_correct_seat(seats,arr_seat):
    '''
    找出客户最前面的那个有票的
    @param seats:
    @param arr_seat:
    @return:
    '''
    seats_require_arr=seats.split(",")
    for seat in seats_require_arr:
        #同样有票的情况下，优先订购第一个
        #下单的时候把想要的放在第一个
        if seat in arr_seat:
            logger.info("First has ticket %s" ,seat)
            return seat

# def handle_seat(qtr,job):
#     logger.info("Handle seat")
#     arr_seat=[]
#     if qtr:
#         # if has_ticket(qtr.hard_seat):
#         #     dic_ticket['hard_seat']=True
#         # if has_ticket(qtr.one_seat):
#         #     dic_ticket['one_seat']=True
#         # if has_ticket(qtr.two_seat):
#         #     dic_ticket['two_seat']=True
#         # if has_ticket(qtr.bussiness_seat):
#         #    dic_ticket['bussiness_seat']=True
#         # if has_ticket(qtr.high_soft_sleeper):
#         #     dic_ticket['high_soft_sleeper']=True
#         # if has_ticket(qtr.soft_sleeper):
#         #     dic_ticket['soft_sleeper']=True
#         # if has_ticket(qtr.dong_sleeper):
#         #     dic_ticket['dong_sleeper']=True
#         # if has_ticket(qtr.hard_sleeper):
#         #     dic_ticket['hard_sleeper']=True
#         # if has_ticket(qtr.soft_seat):
#         #     dic_ticket['soft_seat']=True
#         # if has_ticket(qtr.no_seat):
#         #     dic_ticket['no_seat']=True
#
#         if has_ticket(qtr.hard_seat):
#             arr_seat.append('硬座')
#         if has_ticket(qtr.one_seat):
#             arr_seat.append('一等座')
#         if has_ticket(qtr.two_seat):
#             arr_seat.append('二等座')
#         if has_ticket(qtr.bussiness_seat):
#            arr_seat.append('商务座')
#         if has_ticket(qtr.high_soft_sleeper):
#             arr_seat.append('高级软卧')
#         if has_ticket(qtr.soft_sleeper):
#             arr_seat.append('软卧')
#         if has_ticket(qtr.dong_sleeper):
#             arr_seat.append('动卧')
#         if has_ticket(qtr.hard_sleeper):
#             arr_seat.append('硬卧')
#         if has_ticket(qtr.soft_seat):
#             arr_seat.append('软卧')
#         if has_ticket(qtr.no_seat):
#             arr_seat.append('无座')
#         #dict 排序，优先买价格低的，有座的
#         if arr_seat:
#             logger.info("Exists seat %s ",str(arr_seat))
#             for k in arr_seat:
#                    waitUserArr=dbService.get_wait_user(job.id,DICT_SEAT_MAP[k])
#                    if waitUserArr:
#                       wait_user=waitUserArr[0]
#                       correct_seat=get_correct_seat(wait_user.seats,arr_seat)
#                       logger.info("COrrect seat %s",correct_seat)
#                       if correct_seat:
#                           wait_user.seats=correct_seat
#                       else:
#                           logger.error("Correct seat error")
#                           wait_user.seats=wait_user.seats.splict(",")[0]
#                       orderInfo={}
#                       orderInfo['left_date']=job.left_date
#                       orderInfo['seat']=wait_user.seats
#                       orderInfo['passengers']=wait_user.passengers
#                       orderInfo['secret_str']=qtr.secret_str
#                       orderInfo['left_station']=job.left_station
#                       orderInfo['arrive_station']=job.arrive_station
#                       orderInfo['left_time']=qtr.left_time
#                       logger.info("Order info %s",orderInfo)
#                       order.delay(wait_user.account_key,orderInfo)
#     return
def handle_seat(qtr):
    arr_seat=[]
    if qtr:
        # if has_ticket(qtr.hard_seat):
        #     dic_ticket['hard_seat']=True
        # if has_ticket(qtr.one_seat):
        #     dic_ticket['one_seat']=True
        # if has_ticket(qtr.two_seat):
        #     dic_ticket['two_seat']=True
        # if has_ticket(qtr.bussiness_seat):
        #    dic_ticket['bussiness_seat']=True
        # if has_ticket(qtr.high_soft_sleeper):
        #     dic_ticket['high_soft_sleeper']=True
        # if has_ticket(qtr.soft_sleeper):
        #     dic_ticket['soft_sleeper']=True
        # if has_ticket(qtr.dong_sleeper):
        #     dic_ticket['dong_sleeper']=True
        # if has_ticket(qtr.hard_sleeper):
        #     dic_ticket['hard_sleeper']=True
        # if has_ticket(qtr.soft_seat):
        #     dic_ticket['soft_seat']=True
        # if has_ticket(qtr.no_seat):
        #     dic_ticket['no_seat']=True
        if has_ticket(qtr.hard_seat):
            arr_seat.append('硬座')
        if has_ticket(qtr.two_seat):
            arr_seat.append('二等座')
        if has_ticket(qtr.one_seat):
            arr_seat.append('一等座')
        if has_ticket(qtr.bussiness_seat):
           arr_seat.append('商务座')
        if has_ticket(qtr.high_soft_sleeper):
            arr_seat.append('高级软卧')
        if has_ticket(qtr.soft_sleeper):
            arr_seat.append('软卧')
        if has_ticket(qtr.dong_sleeper):
            arr_seat.append('动卧')
        if has_ticket(qtr.hard_sleeper):
            arr_seat.append('硬卧')
        if has_ticket(qtr.soft_seat):
            arr_seat.append('软卧')
        if has_ticket(qtr.no_seat):
            arr_seat.append('无座')
        #dict 排序，优先买价格低的，有座的
    return arr_seat
def has_ticket(seat):
    if seat=='有':
        return True
    if seat.isdigit() and int(seat) > 0:
        return True
    return False
def checkShouldEnd(job):
    if judge_date_legal(job.left_date,job):
        return True
def checkState(job):
    logger.info("Job state %s",job.state)
    if job.state != QueryJobState.RUNNING.value:
        raise BussinessException
@app.task
def order(order_info,wait_user,retry=0):
    if retry < RETRY:
        wait_user_state=dbService.get_waituser_state(wait_user.id)
        if wait_user_state==WaitUserState.RUNNING.value:
            id=wait_user.id
            userid=wait_user.account_key
            logger.info("Start order %s  %s", order_info, userid)
            affect_row=dbService.change_waituser(id,WaitUserState.ORDERING.value)
            if not affect_row:
                logger.info("Wait user is  ordering by another robot")
                return
            handler = TicketHandler.getTicketHandlerInstance(userid)
            #乐观锁，锁住
            try:
                order_result=handler.order(order_info, userid)
                logger.info("Grabbing order result %s",order_result)
                if order_result:
                   dbService.update_waituser_result(id,WaitUserState.END.value,True,"恭喜你，抢票成功")
                   #异步发送通知，一般短信接口都限ip
                   user=dbService.getAccount(userid)
                   order_info['username']=user.username
                else:
                   #重置锁
                   dbService.update_waituser_result(id,WaitUserState.RUNNING.value,False,'正在运行中')
                return
            except Exception as e:
                #根据异常情况，判断是否做重置
                logger.exception("Occur exception %s",e)
                #注意return
                if isinstance(e,BussinessException):
                   if e.message =='车票信息已过期，请重新查询最新车票信息':
                      dbService.update_waituser_result(id,WaitUserState.END.value,False,'车票信息已过期，请重新查询最新车票信息')
                      return
                   if e.message =='发车前两小时禁止网络售票':
                      dbService.update_waituser_result(id, WaitUserState.END.value, False, '发车前两小时禁止网络售票')
                      return
                   if e.message=='您取消次数过多,今日将不能继续受理您的订票请求':
                       dbService.update_waituser_result(id,WaitUserState.TODAY_BLOCK.value,False,'您今日取消次数过多,明日继续为你抢票。')
                       return
                   if e.message=='Get passengers error':
                      dbService.update_waituser_result(id,WaitUserState.RUNNING.value,False,'正在运行中')
                      time.sleep(5)
                      order.delay(order_info,wait_user,retry=retry+1)
                      return
                #继续执行
                dbService.update_waituser_result(id,WaitUserState.RUNNING.value,False,'正在运行中')
            logger.info("End order")
            return
        logger.info("Wait user is close")

def doRunning(job):
    while (True):
        try:
            checkState(job)
            if checkShouldEnd(job):
               job.state=QueryJobState.END.value
               break
            # 防止ip被屏蔽
            time.sleep(sleep_time)
            logger.info("Sleep %s seconds",sleep_time)
            logger.info("Query by date %s ", job.__dict__)
            trainArr=TicketHandler.query_by_date(job)
            if trainArr:
                logger.info("Query by date response %s", trainArr[0].__dict__)
                handle_seat(trainArr[0],job)
            else:
                logger.info("Query by date response is empty")
            #检查票数的座位，如果有，则下单
            job.count=job.count+1
            logger.info("Add job count ")
            cacheService.save_job(job)
            logger.info("Save to redis")
            dbService.save_job(job)
            logger.info("Save to db")
        except Exception as e:
            #时间错误
            logger.exception(e)
            # if e.message=='乘车日期错误，比当前时间还早!' or e.message=='乘车日期错误，超出一个月预售期':
            #     print("Error",e.message)
            #     break
            #网络错误
            #没有这个车次
@app.task
def push_worker_queue():
    jobArr=dbService.get_job(QueryJobState.START.value)
    print("Job array",jobArr)
    for item in jobArr:
        date_now = datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        date_query = datetime.datetime.combine(item.left_date,datetime.datetime.max.time())
        item.state=QueryJobState.RUNNING.value
        dbService.save_job(item)
        diff = (date_query - date_now).days
        if diff >= 0:
            url = LEFT_TICKETS.get('url').format(left_date=item.left_date, left_station=item.left_station,
                                                 arrive_station=item.arrive_station, type='leftTicket/query')
            logger.info("Push url %s",item.train_number)
            cacheService.lpush('spider12306:start_urls',url)
        else:
            logger.info("Train mumber %s should be end", item.train_number)
            item.state=QueryJobState.END.value
            dbService.save_job(item)
    #把过期的用户车次更新
    dbService.do_expire_waituser(WaitUserState.END.value,'很抱歉，未为您抢到票')
    dbService.do_expire_queryjob()
    logger.info("End expire wait user")
if __name__ == '__main__':
    dbService.do_expire_waituser(WaitUserState.END.value,'很抱歉，未为您抢到票')




