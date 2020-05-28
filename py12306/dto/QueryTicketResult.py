from web.libs.mixins import ModelDictMixin
class QueryTicketResult(ModelDictMixin):
    secret_str=''
    no = 0
    num = 0
    seat_types = ''
    from_station_no = 0
    to_station_no = 0
    left_station = ''
    arrive_station = ''
    left_date = ''
    left_time = ''
    arrive_time = ''
    time = 0
    arrive_at_current_day = 'N'
    bussiness_seat = ''
    one_seat = ''
    two_seat = ''
    high_soft_sleeper = ''
    soft_sleeper = ''
    dong_sleeper = ''
    hard_sleeper = ''
    soft_seat = ''
    hard_seat = ''
    no_seat = ''
    other = ''
    ops=''