from py12306.query import  job
from py12306.dto.QueryJob import QueryJobGrabbing
from py12306.helpers.TicketHandler import TicketHandler
from py12306.helpers.station import Station
from py12306.helpers.db_service import DbService
from task.grabbing import doRunning
dbService=DbService()
if __name__ == '__main__':
    # for i in range(200):
    #     print(add.delay(1,2))

    #job(QueryJob(1,2,3))
    jobGrabbing=QueryJobGrabbing('1','2020-05-27','合肥','苏州','G753',2,1)
    #print(TicketHandler.query_by_date(jobGrabbing))
   # dbService.save_job(jobGrabbing)
    doRunning(jobGrabbing)



