from py12306.dto.QueryJob import QueryJobGrabbing,QueryJobState
import datetime
from py12306.helpers.TicketHandler import TicketHandler
import time
from py12306.exceptions.BussinessException import BussinessException
from py12306.helpers.QueryTrainConfig import judge_date_legal
from multiprocessing import Process
from task.cerely import app
from py12306.helpers.cache_service import CacheService
from py12306.helpers.db_service import DbService
from task.logging_facory import getLogger
dbService=DbService()
cacheService=CacheService()
logger=getLogger(__name__)
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
            time.sleep(5)
            logger.info("Sleep 10 seconds")
            logger.info("Query by date %s ", job.__dict__)
            trainArr=TicketHandler.query_by_date(job)
            logger.info("Train arr %s",str(trainArr))
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
            if e.message=='乘车日期错误，比当前时间还早!' or e.message=='乘车日期错误，超出一个月预售期':
                print("Error",e.message)
                break
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




