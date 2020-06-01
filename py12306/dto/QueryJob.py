from enum import Enum
from py12306.helpers.station import Station
STATE_CHOICES=((0, 'NEW'),(1, 'START'), (2,'RUNNING'), (3,'BLOCK'), (4,'END'))

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
    def __init__(self,id,job_key,account_key,passengers,allow_less_member,seats) -> None:
        super().__init__()
        self.id=id
        self.job_key=job_key
        self.account_key=account_key
        self.passengers=passengers
        self.allow_less_member=allow_less_member
        self.seats=seats
