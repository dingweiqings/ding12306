import pymysql
HOST="10.10.10.70"
USER='root'
PASSWORD='123456'
DB='dingtest'
import base64
import datetime
from py12306.dto.QueryJob import QueryJobGrabbing,WaitUser
from DBUtils.PooledDB import PooledDB
from py12306.logging_factory import getLogger
logger=getLogger(__name__)
pool = PooledDB(pymysql,5,host=HOST,user=USER,passwd=PASSWORD,db=DB,port=3306,setsession=['SET AUTOCOMMIT = 1']) # 5为连接池里的最少连接数，setsession=['SET AUTOCOMMIT = 1']是用来设置线程池是否打开自动更新的配置，0为False，1为True

class UserInfo:
      id=''
      username=''
      password=''
      password_ticket=''

class DbService:
      def getAccount(self,id):
          conn = pool.connection()  #以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          try:
              sql="select * from app_admin_account where id=%s"
              cursor.execute(sql,[id])
              ret1 = cursor.fetchone()  # 取一条
              account=UserInfo()
              account.id= ret1[0]
              account.username=ret1[4]
              account.password =ret1[1]
              account.password_ticket=bytes.decode(base64.b64decode(ret1[17]))
              return account
          except Exception as e:
                print(e)
          finally:
              cursor.close()
              conn.close()
      def save_job(self,job):
          conn = pool.connection()  #以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          print(job.__dict__)
          print(type(job.state))
          try:
              sql="update app_admin_queryjob set state=%s,count=%s where id=%s"
              cursor.execute(sql, [job.state,job.count,job.id])
              conn.commit()
              return cursor.rowcount
          except Exception as e:
                conn.rollback()
                print(e)
          finally:
              cursor.close()
              conn.close()
      def do_expire_queryjob(self):
          conn = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          current_date=datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
          try:
              # running 状态才抢票，正在ordering 或者已经结束的终止
              sql = 'update app_admin_queryjob set state=4 where left_date <%s'
              cursor.execute(sql, [current_date])
              conn.commit()
          except Exception as e:
              conn.rollback()
              print(e)
          finally:
              cursor.close()
              conn.close()

      def do_expire_waituser(self,state,reason):
          conn = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          current_date=datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
          try:
              # running 状态才抢票，正在ordering 或者已经结束的终止
              sql = 'update app_admin_waituser set state=%s,result=%s,reason=%s where left_date < %s '
              cursor.execute(sql, [state,False,reason,current_date])
              conn.commit()
          except Exception as e:
              conn.rollback()
              print(e)
          finally:
              cursor.close()
              conn.close()
      #启动爬虫查询任务是2
      #定时任务查询state是1的
      def get_job(self,state):
          conn = pool.connection()  #以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          resultArr = []
          try:
              sql="select id,left_date,left_station,arrive_station,train_number,state,count from app_admin_queryjob where state=%s"
              cursor.execute(sql,[state])
              allRow=cursor.fetchall()
              for row in allRow:
                  logger.info("Db row %s",str(row))
                  resultArr.append(QueryJobGrabbing(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
          except Exception as e:
                print(e)
          finally:
              cursor.close()
              conn.close()
          return resultArr
      def get_wait_user(self,job_key,seat):
          conn = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          resultArr = []
          try:
              sql = 'SELECT id,job_key,account_key,passengers,allow_less_member,seats FROM app_admin_waituser WHERE job_key=%s AND FIND_IN_SET(%s,seats) ORDER BY `order` desc LIMIT 1 OFFSET 0'
              cursor.execute(sql, [job_key,seat])
              allRow = cursor.fetchall()
              for row in allRow:
                  logger.info("Db row",str(row))
                  resultArr.append(WaitUser(row[0], row[1], row[2], row[3], row[4], row[5]))
          except Exception as e:
              print(e)
          finally:
              cursor.close()
              conn.close()
          return resultArr
      def get_wait_user_scrapy(self,train_numer,seat,start_station,arrive_station,left_date):
          conn = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          try:
              #running 状态才抢票，正在ordering 或者已经结束的终止
              sql = 'SELECT id,job_key,account_key,passengers,allow_less_member,seats,left_date FROM app_admin_waituser WHERE train_number=%s AND FIND_IN_SET(%s,seats) AND left_station=%s AND arrive_station=%s AND left_date=%s AND state=0 ORDER BY `order` desc LIMIT 1 OFFSET 0'
              cursor.execute(sql, [train_numer,seat,start_station,arrive_station,left_date])
              allRow = cursor.fetchall()
              for row in allRow:
                  logger.info("Db row %s",str(row))
                  return WaitUser(row[0], row[1], row[2], row[3], row[4], row[5],row[6])
          except Exception as e:
              print(e)
          finally:
              cursor.close()
              conn.close()
      def get_waituser_state(self,id):
          conn = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          try:
              #running 状态才抢票，正在ordering 或者已经结束的终止
              sql = 'select state from app_admin_waituser where id=%s'
              cursor.execute(sql, [id])
              row=cursor.fetchone()
              return row[0]
          except Exception as e:
              print(e)
          finally:
              cursor.close()
              conn.close()
      def change_waituser(self,id,state):
          conn = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          try:
              #running 状态才抢票，正在ordering 或者已经结束的终止
              sql = 'update app_admin_waituser set state=%s where id=%s'
              affect_row=cursor.execute(sql, [state,id])
              logger.info("Change wait user Affect row %s",affect_row)
              conn.commit()
              return affect_row
          except Exception as e:
              conn.rollback()
              print(e)
          finally:
              cursor.close()
              conn.close()
          return 0
      def update_waituser_result(self, id, state,result,reason):
          conn = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
          cursor = conn.cursor()
          try:
              # running 状态才抢票，正在ordering 或者已经结束的终止
              sql = 'update app_admin_waituser set state=%s,result=%s,reason=%s where id=%s'
              cursor.execute(sql, [state,result,reason,id])
              conn.commit()
          except Exception as e:
              conn.rollback()
              print(e)
          finally:
              cursor.close()
              conn.close()
if __name__ == '__main__':
    r=base64.b64decode('cGEyNzk1NDhzcw==')
    print(bytes.decode(r))
