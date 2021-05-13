import sys;
sys.path.append("..")
from task.addTask import add
if __name__ == '__main__':
    # for i in range(200):
    #     print(add.delay(1,2))

    #job(QueryJob(1,2,3))
    #jobGrabbing=QueryJobGrabbing('1','2020-05-27','合肥','苏州','G753',2,1)
    #print(TicketHandler.query_by_date(jobGrabbing))
   # dbService.save_job(jobGrabbing)
    #doRunning(jobGrabbing)
    add.delay(1,2)



