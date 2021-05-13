import redis
from py12306.config import Config
from py12306.cache_config import *
import pickle
import json
expire=30*60
import requests
import random
class CacheService:
      redis=''
      def __init__(self) -> None:
          super().__init__()
          #内部会使用连接池
          self.redis=redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT,password=Config.REDIS_PASSWORD,db=Config.REDIS_DB)

      def get_cookie(self):
          all_cookies_dict=self.redis.hgetall(COOKIE_MAP)
          valueList=[requests.utils.dict_from_cookiejar(pickle.loads(value)) for key, value in all_cookies_dict.items()]
          if all_cookies_dict:
              return random.choice(valueList)

      def get_ticker_handler(self,userId):
          obj = self.redis.get(TICKET_HANDLER_MAP+":"+userId)
          if obj:
            return pickle.loads(obj)
          return obj
      def set_ticket_handler(self,userId,obj):
          if obj and userId:
              self.redis.set(TICKET_HANDLER_MAP+":"+userId, pickle.dumps(obj),expire)
      def del_ticket_handler(self,userId):
           self.redis.delete(TICKET_HANDLER_MAP+":"+userId)

      def get_ticket_broswer(self,userId):
          obj = self.redis.get(TICKET_BROSWER_MAP+":"+userId)
          if obj:
            return pickle.loads(obj)
          return obj
      def set_ticket_broswer(self,userId,obj):
          if obj and userId:
              self.redis.set(TICKET_BROSWER_MAP+":"+userId, pickle.dumps(obj),expire)
      def del_ticket_broswer(self,userId):
           self.redis.delete(TICKET_BROSWER_MAP+":"+userId)

      def get_api_request(self,jobId):
          obj = self.redis.get(API_REQUEST+":"+jobId)
          if obj:
            return pickle.loads(obj)
          return obj
      def set_api_request(self,jobId,obj):
          if obj and jobId:
              self.redis.set(API_REQUEST+":"+jobId, pickle.dumps(obj),expire)
      def del_api_request(self,jobId):
           self.redis.delete(API_REQUEST+":"+jobId)

      def get_user_info(self,userId):
          obj = self.redis.get(USER_INFO_MAP+":"+userId)
          if obj:
            return pickle.loads(obj)
          return obj
      def set_user_info(self,userId,obj):
          if obj and userId:
             self.redis.set(USER_INFO_MAP+":"+userId,pickle.dumps(obj),expire)
      def del_user_info(self,userId):
           self.redis.delete(USER_INFO_MAP+":"+userId)
      def save_job(self,job):
          if job:
              self.redis.set(QUERY_JOB_MAP+":"+job.id,pickle.dumps(job))
      def del_job(self,id):
           self.redis.delete(QUERY_JOB_MAP+":"+id)
      def get_job(self, id):
          obj=self.redis.get(QUERY_JOB_MAP + ":" + id)
          if obj:
              return pickle.loads(obj)
      def save_task(self,task):
          if task:
              self.redis.set(TASK_MAP+":"+task.id,"NOT_ASSIGN")
      def del_task(self,id):
           self.redis.delete(TASK_MAP+":"+id)
      def get_task(self, id):
          obj=self.redis.get(TASK_MAP + ":" + id)
          return obj
      def get_useful_proxy(self):
          url = 'http://10.10.10.76:5010/get'
          response = requests.get(url)
          body = json.loads(response.text)
          return {'https':body['proxy']}
      def lpush(self, key, value):
          self.redis.lpush(key, value)


