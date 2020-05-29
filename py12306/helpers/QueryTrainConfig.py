from datetime import datetime
from py12306.config import Config
from py12306.helpers.station import Station

from py12306.helpers.func import *

from py12306.dto.QueryTicketResult import QueryTicketResult
# 普通K：21：软卧、 24：无座  25：  26：硬卧  27：硬座  
# 普通T：19:高级软  20：其它  21：软卧  24：无座  26：硬卧  27：硬座
# 普通Z：19:高级软  21：软卧  24：无座  26：硬卧  27：硬座
# 普通Y：22：软座   24：无座  27：硬座
# 高铁G：23：特等   24：无座  28：二等  29：一等  30：商务
# 城际C：23：特等   24：无座  28：二等  29：一等  30：商务 
# 动车D：21：软卧   24：无座  28：二等  29：一等  31：动卧 
#
#
# 其他车：21：软卧  24：无座  26：硬卧  27：硬座
#商务座/特等座 32	一等座31	二等座/二等包座30	高级软卧21 软卧/一等卧23	动卧 	硬卧/二等卧28	  软座	 硬座29 	无座26	其他
# 2 列车是否停运,可以则显示预订
#
from py12306.exceptions.BussinessException import BussinessException
INDEX_BUSSINESS_SEAT= 32
INDEX_ONE_SEAT = 31
INDEX_TWO_SEAT = 30

INDEX_HITH_SOFT_SLEEPER = 21
INDEX_SOFT_SLEEPER = 23  # 4 5 始发 终点
IDNEX_DONG_SLEEPER= 27
INDEX_HARD_SLEEPER = 28
INDEX_SOFT_SEAT = 27  # 下单文字
INDEX_HARD_SEAT = 29
INDEX_NO_SEAT = 26

#查询价格用的seat type
INDEX_SEAT_TYPE=35
IDNEX_FROM_STATION_NO=16
INDEX_TO_STATION_NO=17
INDEX_TICKET_NUM = 11
INDEX_TRAIN_NUMBER = 3
INDEX_TRAIN_NO = 2
INDEX_LEFT_DATE = 13
INDEX_LEFT_STATION = 6  # 4 5 始发 终点
INDEX_ARRIVE_STATION = 7
INDEX_ORDER_TEXT = 1  # 下单文字
INDEX_SECRET_STR = 0
INDEX_LEFT_TIME = 8
INDEX_ARRIVE_TIME = 9
INDEX_TIME=10
INDEX_ARRIVE_AT_CURRENT_DAY=11




def handle_response_query_date(response, trainNum):
        """
        错误判断
        余票判断
        小黑屋判断
        座位判断
        乘车人判断
        :param result:
        :return:
        """
        results = get_results(response)
        resultArr = []
        if not results:
            print(results)
            return []
        for result in results:
            ticket_info = result.split('|')
            num = get_info_of_train_number(ticket_info)
            if trainNum and num != trainNum:
                continue
            qtr = QueryTicketResult()
            qtr.ops = ticket_info[1]
            qtr.secret_str=ticket_info[0]
            if ticket_info[1] != '预订':#列车停运
                qtr.no = get_info_of_train_no(ticket_info)
                qtr.num = get_info_of_train_number(ticket_info)
                qtr.seat_types = "-"
                qtr.from_station_no = "-"
                qtr.to_station_no = "-"
                qtr.left_station = get_info_of_left_station(ticket_info)
                qtr.arrive_station = get_info_of_arrive_station(ticket_info)
                qtr.left_date = "-"
                qtr.left_time = "-"
                qtr.arrive_time = "-"
                qtr.time = "-"
                qtr.arrive_at_current_day = "-"
                qtr.bussiness_seat = "-"
                qtr.one_seat = "-"
                qtr.two_seat = "-"
                qtr.high_soft_sleeper = "-"
                qtr.soft_sleeper = "-"
                qtr.dong_sleeper = "-"
                qtr.hard_sleepr = "-"
                qtr.soft_seat = "-"
                qtr.hard_seat = "-"
                qtr.no_seat = "-"
                qtr.other = "-"
            else:
                qtr.no = get_info_of_train_no(ticket_info)
                qtr.num = get_info_of_train_number(ticket_info)
                qtr.seat_types = get_info_of_seat_type(ticket_info)
                qtr.from_station_no = get_info_of_from_station_no(ticket_info)
                qtr.to_station_no = get_info_of_to_station_no(ticket_info)
                qtr.left_station = get_info_of_left_station(ticket_info)
                qtr.arrive_station = get_info_of_arrive_station(ticket_info)
                qtr.left_date = get_info_of_left_date(ticket_info)
                qtr.left_time = get_info_of_train_left_time(ticket_info)
                qtr.arrive_time = get_info_of_train_arrive_time(ticket_info)
                qtr.time = get_info_of_train_time(ticket_info)
                qtr.arrive_at_current_day = get_info_of_arrive_at_current_day(ticket_info)
                qtr.bussiness_seat = get_info_of_bussiness_seat(ticket_info)
                qtr.one_seat = get_info_of_one_seat(ticket_info)
                qtr.two_seat = get_info_of_two_seat(ticket_info)
                qtr.high_soft_sleeper = get_info_of_train_high_soft_sleeper(ticket_info)
                qtr.soft_sleeper = get_info_of_train_soft_sleeper(ticket_info)
                qtr.dong_sleeper = get_info_of_dong_sleeper(ticket_info)
                qtr.hard_sleeper = get_info_of_hard_sleeper(ticket_info)
                qtr.soft_seat = get_info_of_soft_seat(ticket_info)
                qtr.hard_seat = get_info_of_hard_seat(ticket_info)
                qtr.no_seat = get_info_of_no_seat(ticket_info)
                qtr.other = get_info_of_other(ticket_info)
            resultArr.append(qtr)
            # 处理返回的ticket_info
        return resultArr

def judge_date_legal(date, train_info=None):
  date_now = datetime.datetime.now()
  date_query = datetime.datetime.strptime(str(date), "%Y-%m-%d")
  diff = (date_query - date_now).days
  # 查询日期是过去的时间
  if date_now.day == date_query.day:
      diff = 0
      # 查询日期是当天，发车两小时前停止网络售票
      if train_info:
         if isinstance(train_info,dict):
            left_time=train_info['left_time']
         else:
             left_time=train_info.left_time
         interval=int(left_time.split(":")[0])*60+int(left_time.split(":")[1])-(date_now.hour*60+date_now.minute)
         if interval <=Config.MIN_BUY_TIME:
             raise BussinessException(message="发车前两小时禁止网络售票")
  if diff < 0:
      msg = '乘车日期错误，比当前时间还早!'
      raise BussinessException(message=msg)
  elif diff > Config.MAX_BUY_TIME:
      msg = '乘车日期错误，超出一个月预售期'
      raise BussinessException(message=msg)
def get_results(response):
  """
  解析查询返回结果
  :param response:
  :return:
  """
  result = response.json().get('data.result')
  return result if result else False






# 提供一些便利方法
# 时间
def get_info_of_left_date(ticket_info):
  return ticket_info[INDEX_LEFT_DATE]

def get_info_of_ticket_num(ticket_info):
  return ticket_info[INDEX_TICKET_NUM]

# 车次序列号
def get_info_of_train_no(ticket_info):
  return ticket_info[INDEX_TRAIN_NO]

# 车次
def get_info_of_train_number(ticket_info):
  return ticket_info[INDEX_TRAIN_NUMBER]

def get_info_of_train_no(ticket_info):
  return ticket_info[INDEX_TRAIN_NO]

def get_info_of_left_station(ticket_info):
  return Station().get_station_name_by_key(ticket_info[INDEX_LEFT_STATION])

def get_info_of_arrive_station(ticket_info):
  return Station().get_station_name_by_key(ticket_info[INDEX_ARRIVE_STATION])

def get_info_of_order_text(ticket_info):
  return ticket_info[INDEX_ORDER_TEXT]

def get_info_of_secret_str(ticket_info):
  return ticket_info[INDEX_SECRET_STR]

def get_info_of_train_left_time(ticket_info):
  return ticket_info[INDEX_LEFT_TIME]

def get_info_of_train_arrive_time(ticket_info):
  return ticket_info[INDEX_ARRIVE_TIME]

def get_info_of_train_time(ticket_info):
  return ticket_info[INDEX_TIME]

def get_info_of_arrive_at_current_day(ticket_info):
  return isArriveAtCurrentDay(ticket_info[INDEX_LEFT_TIME],ticket_info[INDEX_TIME])

# 座位
def get_info_of_bussiness_seat(ticket_info):
  return getSeat(ticket_info[INDEX_BUSSINESS_SEAT])

def get_info_of_one_seat(ticket_info):
  return getSeat(ticket_info[INDEX_ONE_SEAT])

def get_info_of_two_seat(ticket_info):
  return getSeat(ticket_info[INDEX_TWO_SEAT])

def get_info_of_train_high_soft_sleeper(ticket_info):
  return getSeat(ticket_info[INDEX_HITH_SOFT_SLEEPER])

def get_info_of_train_soft_sleeper(ticket_info):
  return getSeat(ticket_info[INDEX_SOFT_SLEEPER])

def get_info_of_dong_sleeper(ticket_info):
  return '-'

def get_info_of_hard_sleeper(ticket_info):
  return getSeat(ticket_info[INDEX_HARD_SLEEPER])

def get_info_of_soft_seat(ticket_info):
  return '-'

def get_info_of_hard_seat(ticket_info):
  return getSeat(ticket_info[INDEX_HARD_SEAT])

def get_info_of_no_seat(ticket_info):
  return getSeat(ticket_info[INDEX_NO_SEAT])

def get_info_of_seat_type(ticket_info):
  return ticket_info[INDEX_SEAT_TYPE]

def get_info_of_from_station_no(ticket_info):
  return ticket_info[IDNEX_FROM_STATION_NO]

def get_info_of_to_station_no(ticket_info):
  return ticket_info[INDEX_TO_STATION_NO]

def get_info_of_other(ticket_info):
  return '-'

def getSeat(seat):
  return seat if seat != '' else '-'
def isArriveAtCurrentDay(starttime,peroid):
    hourStart = int(starttime.split(":")[0])
    minute = int(starttime.split(":")[1])
    peroidHour = int(peroid.split(":")[0])
    minutePeroid = int(peroid.split(":")[1])
    return hourStart+peroidHour+ (minute+minutePeroid)//60 < 24
