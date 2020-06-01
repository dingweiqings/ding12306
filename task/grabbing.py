from py12306.dto.QueryJob import QueryJobGrabbing,QueryJobState
import datetime
from py12306.helpers.TicketHandler import TicketHandler
import time
from py12306.exceptions.BussinessException import BussinessException
from py12306.helpers.QueryTrainConfig import judge_date_legal
from task.celery import app
from py12306.helpers.TicketHandler import TicketHandler
from py12306.helpers.cache_service import CacheService
from py12306.helpers.db_service import DbService
from task.order import order
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
sleep_time = 10

@app.task
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



def handle_seat(qtr,job):
    logger.info("Handle seat")
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
        if has_ticket(qtr.one_seat):
            arr_seat.append('一等座')
        if has_ticket(qtr.two_seat):
            arr_seat.append('二等座')
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
        if arr_seat:
            logger.info("Exists seat %s ",str(arr_seat))
            for k in arr_seat:
                   waitUserArr=dbService.get_wait_user(job.id,DICT_SEAT_MAP[k])
                   if waitUserArr:
                      wait_user=waitUserArr[0]
                      correct_seat=get_correct_seat(wait_user.seats,arr_seat)
                      logger.info("COrrect seat %s",correct_seat)
                      if correct_seat:
                          wait_user.seats=correct_seat
                      else:
                          logger.error("Correct seat error")
                          wait_user.seats=wait_user.seats.splict(",")[0]
                      orderInfo={}
                      orderInfo['left_date']=job.left_date
                      orderInfo['seat']=wait_user.seats
                      orderInfo['passengers']=wait_user.passengers
                      orderInfo['secret_str']=qtr.secret_str
                      orderInfo['left_station']=job.left_station
                      orderInfo['arrive_station']=job.arrive_station
                      orderInfo['left_time']=qtr.left_time
                      logger.info("Order info %s",orderInfo)
                      order.delay(wait_user.account_key,orderInfo)
    return
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
def save(job):
    print("Job block,save")
@app.task
def push_worker_queue():
    jobArr=dbService.get_job()
    print("Job array",jobArr)
    for job in jobArr:
        #防止重复添加
        job.state=2
        dbService.save_job(job)
        grabbing.delay(job)




