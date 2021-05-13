from enum import Enum
from py12306.helpers.station import Station
STATE_CHOICES=((0, 'NEW'),(1, 'START'), (2,'RUNNING'), (3,'BLOCK'), (4,'END'))
WAIT_STATE_CHOICES=((0,'RUNNING'),(1,'ORDERING'),(2,'END'))

class WaitUserState(Enum):
    RUNNING = 0
    ORDERING = 1
    TODAY_BLOCK=2
    END = 3


class QueryJobState(Enum):
    NEW = 0
    START = 1
    RUNNING = 2
    BLOCK = 3
    END = 4
class QueryJobState(Enum):
       NEW=0
       START= 1
       RUNNING=2
       BLOCK=3
       END=4
class QueryJobGrabbing:
        id=''
        left_date=''
        left_station=''
        arrive_station=''
        train_number=''
        state=''
        count=0
        def __init__(self,id,left_date,left_station,arrive_station,train_number,state,count) -> None:
            super().__init__()
            self.id=id
            self.left_date=left_date
            self.left_station=Station.get_station_key_by_name(left_station)
            self.arrive_station=Station.get_station_key_by_name(arrive_station)
            self.train_number=train_number
            self.state=state
            self.count=count
class WaitUser:
    id =''
    job_key =''
    account_key = ''
    passengers = ''
    allow_less_member = ''
    seats = ''
    left_date=''
    def __init__(self,id,job_key,account_key,passengers,allow_less_member,seats,left_date) -> None:
        super().__init__()
        self.id=id
        self.job_key=job_key
        self.account_key=account_key
        self.passengers=passengers
        self.allow_less_member=allow_less_member
        self.seats=seats
        self.left_date=left_date
if __name__ == '__main__':
    import datetime
    date_now = datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d"),"%Y-%m-%d")
    date_query = datetime.datetime.strptime('2020-06-17', "%Y-%m-%d")
    diff = (date_query-date_now).days
    print(diff)