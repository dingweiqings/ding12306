import sys
from datetime import timedelta
from datetime import datetime

from py12306.app import app_available_check
from py12306.cluster.cluster import Cluster
from py12306.config import Config
from py12306.helpers.api import LEFT_TICKETS
from py12306.helpers.station import Station
from py12306.helpers.type import OrderSeatType, SeatType
from py12306.log.query_log import QueryLog
from py12306.helpers.func import *
from py12306.log.user_log import UserLog
from py12306.order.order import Order
from py12306.user.user import User
from py12306.helpers.event import Event
from web.app_admin.models import QueryJob,QueryJobState


#class QueryTask:
"""
查询任务
"""
id = 0
is_alive = True
job_name = None
left_dates = []
left_date = None
stations = []
left_station = ''
arrive_station = ''
left_station_code = ''
arrive_station_code = ''
from_time = timedelta(hours=0)
to_time = timedelta(hours=24)

account_key = 0
allow_seats = []
current_seat = None
current_seat_name = ''
current_order_seat = None
allow_train_numbers = []
except_train_numbers = []
members = []
member_num = 0
member_num_take = 0  # 最终提交的人数
passengers = []
allow_less_member = False
retry_time = 3

interval = {}
interval_additional = 0
interval_additional_max = 5

query = None
cluster = None
ticket_info = {}
is_cdn = False
query_time_out = 3
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

max_buy_time = 32


    # def __init__(self, info, query):
    #     self.cluster = Cluster()
    #     self.query = query
    #     self.init_data(info)
    #     self.update_interval()
    #
    # def init_data(self, info):
    #     self.id = md5(info)
    #     self.left_dates = info.get('left_dates')
    #     self.stations = info.get('stations')
    #     self.stations = [self.stations] if isinstance(self.stations, dict) else self.stations
    #     if not self.job_name:  # name 不能被修改
    #         self.job_name = info.get('job_name',
    #                                  '{} -> {}'.format(self.stations[0]['left'], self.stations[0]['arrive']))
    #
    #     self.account_key = str(info.get('account_key'))
    #     self.allow_seats = info.get('seats')
    #     self.allow_train_numbers = info.get('train_numbers')
    #     self.except_train_numbers = info.get('except_train_numbers')
    #     self.members = list(map(str, info.get('members')))
    #     self.member_num = len(self.members)
    #     self.member_num_take = self.member_num
    #     self.allow_less_member = bool(info.get('allow_less_member'))
    #     period = info.get('period')
    #     if isinstance(period, dict):
    #         if 'from' in period:
    #             parts = period['from'].split(':')
    #             if len(parts) == 2:
    #                 self.from_time = timedelta(
    #                     hours=int(parts[0]), seconds=int(parts[1]))
    #         if 'to' in period:
    #             parts = period['to'].split(':')
    #             if len(parts) == 2:
    #                 self.to_time = timedelta(
    #                     hours=int(parts[0]), seconds=int(parts[1]))
def start(self,queryjob):
    """
    处理单个任务
    根据日期循环查询, 展示处理时间
    :param job:
    :return:
    """
    if not isinstance(queryjob,QueryJob):
        return
    while True and queryjob.status!= QueryJobState.END:
        id = md5(queryjob)
        left_dates = queryjob.getattr('left_date')
        stations = queryjob.getattr('stations')
        stations = [stations] if isinstance(stations, dict) else stations
        #数据处理
        left_station = stations.split("-")[0]
        arrive_station = stations.split("-")[1]
        if not job_name:  # name 不能被修改
            job_name = queryjob.getattr('job_name',
                                        '{} -> {}'.format(left_station,arrive_station))

        account_key = str(queryjob.getattr('account_key'))
        allow_seats = queryjob.getattr('seats')
        allow_train_numbers = queryjob.getattr('train_numbers')
        except_train_numbers = queryjob.getattr('except_train_numbers')
        members = queryjob.getattr('members').split(",")
        member_num = len(members)
        member_num_take = member_num
        allow_less_member = bool(queryjob.getattr('allow_less_member'))
        period = queryjob.getattr('period')
        from_time = 0
        to_time = 24
        if period:
            peroidArr=period.split(",");
            #先取第一个
            from_time=int(period[0].split("-")[0])
            to_time=int(period[0].split("-")[1])
        # if isinstance(period, dict):
        #     if 'from' in period:
        #         parts = period['from'].split(':')
        #         if len(parts) == 2:
        #             from_time = timedelta(
        #                 hours=int(parts[0]), seconds=int(parts[1]))
        #     if 'to' in period:
        #         parts = period['to'].split(':')
        #         if len(parts) == 2:
        #             to_time = timedelta(
        #                 hours=int(parts[0]), seconds=int(parts[1]))
        app_available_check()
        QueryLog.print_job_start(queryjob['id']+job_name)
        refresh_station(stations)

        response = query_by_date(left_dates,stations)
        handle_response(response)
        QueryLog.add_query_time_log(time=response.elapsed.total_seconds(), is_cdn=Config.is_cdn_enabled())
        #状态监控
        safe_stay()
        if is_main_thread():
            QueryLog.flush(sep='\t\t', publish=False)


        if not Config().QUERY_JOB_THREAD_ENABLED:
            QueryLog.add_quick_log('').flush(publish=False)
            break
        else:
            QueryLog.add_log('\n').flush(sep='\t\t', publish=False)
        if Const.IS_TEST: return
def judge_date_legal(self, date):
    date_now = datetime.datetime.now()
    date_query = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    diff = (date_query - date_now).days
    if date_now.day == date_query.day:
        diff = 0
    if diff < 0:
        msg = '乘车日期错误，比当前时间还早！！'
        QueryLog.add_quick_log(msg).flush(publish=False)
        raise RuntimeError(msg)
    elif diff > self.max_buy_time:
        msg = '乘车日期错误，超出一个月预售期！！'
        QueryLog.add_quick_log(msg).flush(publish=False)
        raise RuntimeError(msg)
    else:
        pass
def refresh_station(stations):
    left_station = stations.split("-")[0]
    arrive_station = stations.split("-")[1]
    left_station_code = Station.get_station_key_by_name(left_station)
    arrive_station_code = Station.get_station_key_by_name(arrive_station)
def query_by_date(date,stations):
    """
    通过日期进行查询
    :return:
    """
    left_station = stations.split("-")[0]
    arrive_station = stations.split("-")[1]
    left_station_code = Station.get_station_key_by_name(left_station)
    arrive_station_code = Station.get_station_key_by_name(arrive_station)
    judge_date_legal(date)
    from py12306.helpers.cdn import Cdn
    QueryLog.add_log(('\n' if not is_main_thread() else '') + QueryLog.MESSAGE_QUERY_START_BY_DATE.format(date,
                                                                                                          left_station,
                                                                                                          arrive_station))
    url = LEFT_TICKETS.get('url').format(left_date=date, left_station=left_station_code,
                                         arrive_station=arrive_station_code, type='api')
    #开启cdn
    if Config.is_cdn_enabled() and Cdn().is_ready:
        return query.session.cdn_request(url, timeout=query_time_out, allow_redirects=False)
    return query.session.get(url, timeout=query_time_out, allow_redirects=False)

def handle_response(response):
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
    if not results:
        return False
    for result in results:
        ticket_info = result.split('|')
        if not is_trains_number_valid():  # 车次是否有效
            continue
        QueryLog.add_log(QueryLog.MESSAGE_QUERY_LOG_OF_EVERY_TRAIN.format(get_info_of_train_number()))
        if not is_has_ticket(ticket_info):
            continue
        allow_seats = allow_seats if allow_seats else list(
            Config.SEAT_TYPES.values())  # 未设置 则所有可用 TODO  合法检测
        handle_seats(allow_seats, ticket_info)

def handle_seats( allow_seats, ticket_info):
    for seat in allow_seats:  # 检查座位是否有票
        set_seat(seat)
        ticket_of_seat = ticket_info[current_seat]
        if not is_has_ticket_by_seat(ticket_of_seat):  # 座位是否有效
            continue
        QueryLog.print_ticket_seat_available(left_date=get_info_of_left_date(),
                                             train_number=get_info_of_train_number(), seat_type=seat,
                                             rest_num=ticket_of_seat)
        if not is_member_number_valid(ticket_of_seat):  # 乘车人数是否有效
            if allow_less_member:
                member_num_take = int(ticket_of_seat)
                QueryLog.print_ticket_num_less_than_specified(ticket_of_seat)
            else:
                QueryLog.add_quick_log(
                    QueryLog.MESSAGE_GIVE_UP_CHANCE_CAUSE_TICKET_NUM_LESS_THAN_SPECIFIED).flush()
                continue
        #
        if Const.IS_TEST: return
        # 检查完成 开始提交订单
        QueryLog.print_ticket_available(left_date=get_info_of_left_date(),
                                        train_number=get_info_of_train_number(),
                                        rest_num=ticket_of_seat)
        if User.is_empty():
            QueryLog.add_quick_log(QueryLog.MESSAGE_USER_IS_EMPTY_WHEN_DO_ORDER.format(retry_time))
            return stay_second(retry_time)

        order_result = False
        user = get_user()
        if not user:
            QueryLog.add_quick_log(QueryLog.MESSAGE_ORDER_USER_IS_EMPTY.format(retry_time))
            return stay_second(retry_time)

        lock_id = Cluster.KEY_LOCK_DO_ORDER + '_' + user.id
        if cluster.get_lock(lock_id, Cluster.lock_do_order_time,
                                 {'node': cluster.node_name}):  # 获得下单锁
            order_result = do_order(user)
            if not order_result:  # 下单失败，解锁
                cluster.release_lock(lock_id)
        else:
            QueryLog.add_quick_log(
                QueryLog.MESSAGE_SKIP_ORDER.format(cluster.get_lock_info(lock_id).get('node'),
                                                   user.user_name))
            stay_second(retry_time)  # 防止过多重复

        # 任务已成功 通知集群停止任务
        if order_result:
            sendEmail()
            #Event().job_destroy({'name': job_name})
def sendEmail():
    print("send email")
def do_order(user):
    check_passengers()
    order = Order(user=user)
    return order.order()

def get_results(response):
    """
    解析查询返回结果
    :param response:
    :return:
    """
    interval_additional = 0
    interval_additional_max = 5
    if response.status_code != 200:
        QueryLog.print_query_error(response.reason, response.status_code)
        if interval_additional < interval_additional_max:
            interval_additional += interval.get('min')
    else:
        interval_additional = 0
    result = response.json().get('data.result')
    return result if result else False

def is_has_ticket(ticket_info):
    return get_info_of_ticket_num() == 'Y' and get_info_of_order_text() == '预订'

def is_has_ticket_by_seat(seat):
    return seat != '' and seat != '无' and seat != '*'
#TODO
def is_trains_number_valid():
    train_left_time = get_info_of_train_left_time()
    time_parts = train_left_time.split(':')
    left_time = timedelta(
        hours=int(time_parts[0]), seconds=int(time_parts[1]))
    if left_time < from_time or left_time > to_time:
        return False

    if except_train_numbers:
        return get_info_of_train_number().upper() not in map(str.upper, except_train_numbers)
    if allow_train_numbers:
        return get_info_of_train_number().upper() in map(str.upper,allow_train_numbers)
    return True

def is_member_number_valid(seat):
    return seat == '有' or self.member_num <= int(seat)

def destroy(self):
    """
    退出任务
    :return:
    """
    from py12306.query.query import Query
    self.is_alive = False
    QueryLog.add_quick_log(QueryLog.MESSAGE_QUERY_JOB_BEING_DESTROY.format(self.job_name)).flush()
    # sys.exit(1) # 无法退出线程...
    # 手动移出jobs 防止单线程死循环
    index = Query().jobs.index(self)
    Query().jobs.pop(index)

def safe_stay():
    origin_interval = get_interval_num(interval)
    interval = origin_interval + interval_additional
    QueryLog.add_stay_log(
        '%s + %s' % (origin_interval, interval_additional) if interval_additional else origin_interval)
    stay_second(interval)

def set_passengers(passengers):
    UserLog.print_user_passenger_init_success(passengers)
    passengers = passengers

def set_seat(self, seat):
    self.current_seat_name = seat
    self.current_seat = SeatType.dicts.get(seat)
    self.current_order_seat = OrderSeatType.dicts.get(seat)

def get_user(self):
    user = User.get_user(self.account_key)
    # if not user.check_is_ready(): # 这里不需要检测了，后面获取乘客时已经检测过
    #     #
    #     pass
    return user

def check_passengers(self):
    if not self.passengers:
        QueryLog.add_quick_log(QueryLog.MESSAGE_CHECK_PASSENGERS.format(self.job_name)).flush()
        passengers = User.get_passenger_for_members(self.members, self.account_key)
        if passengers:
            self.set_passengers(passengers)
        else:  # 退出当前查询任务
            self.destroy()
    return True

def refresh_station(self, station):
    self.left_station = station.get('left')
    self.arrive_station = station.get('arrive')
    self.left_station_code = Station.get_station_key_by_name(self.left_station)
    self.arrive_station_code = Station.get_station_key_by_name(self.arrive_station)

# 提供一些便利方法
def get_info_of_left_date(self):
    return self.ticket_info[self.INDEX_LEFT_DATE]

def get_info_of_ticket_num(self):
    return self.ticket_info[self.INDEX_TICKET_NUM]

def get_info_of_train_number(self):
    return self.ticket_info[self.INDEX_TRAIN_NUMBER]

def get_info_of_train_no(self):
    return self.ticket_info[self.INDEX_TRAIN_NO]

def get_info_of_left_station(self):
    return Station.get_station_name_by_key(self.ticket_info[self.INDEX_LEFT_STATION])

def get_info_of_arrive_station(self):
    return Station.get_station_name_by_key(self.ticket_info[self.INDEX_ARRIVE_STATION])

def get_info_of_order_text(self):
    return self.ticket_info[self.INDEX_ORDER_TEXT]

def get_info_of_secret_str(self):
    return self.ticket_info[self.INDEX_SECRET_STR]

def get_info_of_train_left_time(self):
    return self.ticket_info[self.INDEX_LEFT_TIME]

def get_info_of_train_arrive_time(self):
    return self.ticket_info[self.INDEX_ARRIVE_TIME]
