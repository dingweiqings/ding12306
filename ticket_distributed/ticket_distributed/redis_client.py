import redis
from ticket_distributed.settings import REDIS_HOST,REDIS_PARAMS,REDIS_PORT
from py12306.helpers.db_service import DbService
from py12306.helpers.station import Station
from py12306.helpers.api import LEFT_TICKETS
from py12306.dto.QueryJob import QueryJobState
dbService=DbService()
import datetime
class RedisClient:
    redis = ''

    def __init__(self) -> None:
        super().__init__()
        # 内部会使用连接池
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,password=REDIS_PARAMS['password'])
    def lpush(self,key,value):
        self.redis.lpush(key,value)

    def init_job(self,key):
        resultArr=dbService.get_job(QueryJobState.RUNNING.value)
        for item in resultArr:
            date_now = datetime.datetime.now()
            date_query = datetime.datetime.combine(item.left_date, datetime.datetime.max.time())
            diff = (date_query - date_now).days
            if diff >= 0:
                url = LEFT_TICKETS.get('url').format(left_date=item.left_date, left_station=item.left_station,
                                                     arrive_station=item.arrive_station, type='leftTicket/query')
                self.lpush(key, url)
