import pickle
import re
from os import path
from py12306.helpers.api import *
from py12306.helpers.auth_code import AuthCode
from py12306.helpers.request import Request
from py12306.helpers.type import UserType
from py12306.helpers.QueryTrainConfig import *
from py12306.log.order_log import OrderLog
from py12306.log.user_log import UserLog
from py12306.log.common_log import CommonLog
from py12306.helpers.cache_service import CacheService
from py12306.order.order import Order
# 封装12306 需要登录的操作
from py12306.exceptions.BussinessException import BussinessException
from py12306.helpers.db_service import DbService
from py12306.helpers.type import OrderSeatType, SeatType
from py12306.dto.QueryJob import QueryJobGrabbing
cacheService = CacheService()
dbService=DbService()
from py12306.logging_factory import getLogger
logger=getLogger(__name__)
class TicketBroswer:
    # heartbeat = 60 * 2  # 心跳保持时长
    user_name = ''
    password = ''
    info = {}  # 用户信息
    user_loaded = False  # 用户是否已加载成功
    passengers = []
    retry_time = 5
    login_num = 0  # 尝试登录次数
    #密码超过4次则会被锁定
    max_retry_num= 3
    # Init page
    global_repeat_submit_token = None
    ticket_info_for_passenger_form = None
    order_request_dto = None
    lock_init_user_time = 3 * 60
    cookie = False
    local = threading.local()
    cacheService=''
    def __init__(self, info):
        self.init_data(info)

    def init_data(self, info):
        self.session = Request()
        #self.session.add_response_hook(self.response_login_check)
        self.key = info.id
        self.user_name = info.username
        self.password = info.password_ticket
        #self.handle_login()

    # def getUserLoginDTO(self):
    #     return {"username": "D13340124151148","password": "pa279548ss"}
    def postHtml(self,url,data,params=None):
        #self.handle_login()
        print(url,data,params)
        response = self.session.post(url, data,params)
        return response
    def getHtml(self,url,params):
        # 处理login 和cookie
        #self.handle_login()
        print(url, params)
        response = self.session.get(url,params=params)
        return response
    def post(self,url,data,params=None):
        #需要处理12306 session 过期的情况
        #self.handle_login()
        logger.info("%s %s %s",url,data,params)
        response = self.session.post(url, data,params)
        return self.handle_response(response)
    def get(self,url,params):
        # 处理login 和cookie
        #self.handle_login()
        logger.info("%s %s",url, params)
        response = self.session.get(url,params=params)
        return self.handle_response(response)
    # def init_cookies
    def is_first_time(self):
        return not path.exists(self.get_cookie_path())

    def handle_login(self):
        if not self.check_user_is_login():
            logger.info("Not login ,next login")
            self.login()
    def login(self,login_num=0):
        if login_num > self.max_retry_num:
            raise BussinessException(message="Max login retry num exceed")
        """
        获取验证码结果
        :return 权限校验码
        """
        print("start login")
        data = {
            'username': self.user_name,
            'password': self.password,
            'appid': 'otn'
        }
        answer = AuthCode.get_auth_code(self.session)
        data['answer'] = answer
        self.request_device_id()
        response = self.session.post(API_BASE_LOGIN.get('url'), data)
        result = response.json()
        if result.get('result_code') == 0:  # 登录成功
            """
            login 获得 cookie uamtk
            auth/uamtk      不请求，会返回 uamtk票据内容为空
            /otn/uamauthclient 能拿到用户名
            """
            new_tk = self.auth_uamtk()
            user_name = self.auth_uamauthclient(new_tk)
            self.update_user_info({'user_name': user_name})
            self.session.cookies.update(response.cookies)  # 保存cookie
            self.login_did_success()
            return True
        elif result.get('result_code') == 2:  # 账号密码错误
            # 登录失败，用户名或密码为空
            # 密码输入错误
            raise BussinessException(message="username or password error")
            UserLog.add_quick_log(UserLog.MESSAGE_LOGIN_FAIL.format(result.get('result_message'))).flush()
            login_num = login_num + 1
        else:
            login_num = login_num + 1
            UserLog.add_quick_log(
                UserLog.MESSAGE_LOGIN_FAIL.format(result.get('result_message', result.get('message','Response json body is empty',
                                                                                 CommonLog.MESSAGE_RESPONSE_EMPTY_ERROR)))).flush()
            self.login(login_num=login_num)
    #检查登录状态
    def check_user_is_login(self):
        response = self.session.post(API_USER_LOGIN_CHECK)
        #is_login = response.json().get('data.is_ogin', False) == 'Y'
        logger.info("Check user login %s", response.text)
        is_login = response.json().get('data.is_login', False) == 'Y'
        if is_login:
            #self.save_user()
            logger.info("User has already login to 12306 ")
            #return self.get_user_info()  # 检测应该是不会维持状态，这里再请求下个人中心看有没有用，01-10 看来应该是没用  01-22 有时拿到的状态 是已失效的再加上试试
        else:
            logger.info("Still no login")
            pass
        return is_login

    def auth_uamtk(self):
        response = self.session.post(API_AUTH_UAMTK.get('url'), {'appid': 'otn'}, headers={
            'Referer': 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin',
            'Origin': 'https://kyfw.12306.cn'
        })
        result = response.json()
        if result.get('newapptk'):
            return result.get('newapptk')
        # TODO 处理获取失败情况
        return False

    def auth_uamauthclient(self, tk):
        response = self.session.post(API_AUTH_UAMAUTHCLIENT.get('url'), {'tk': tk})
        result = response.json()
        if result.get('username'):
            return result.get('username')
        # TODO 处理获取失败情况
        return False

    def request_device_id(self):
        """
        获取加密后的浏览器特征 ID
        :return:
        """
        response = self.session.get(API_GET_BROWSER_DEVICE_ID)
        if response.status_code == 200:
            try:
                result = json.loads(response.text)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
                }
                from base64 import b64decode
                self.session.headers.update(headers)
                response = self.session.get(b64decode(result['id']).decode())
                if response.text.find('callbackFunction') >= 0:
                    result = response.text[18:-2]
                result = json.loads(result)
                if  Config().is_cache_rail_id_enabled():
                   self.session.cookies.update({
                       'RAIL_EXPIRATION': result.get('exp'),
                       'RAIL_DEVICEID': result.get('dfp'),
                   })
                else:
                   self.session.cookies.update({
                       'RAIL_EXPIRATION': Config().RAIL_EXPIRATION,
                       'RAIL_DEVICEID': Config().RAIL_DEVICEID,
                   })
            except:
                return False

    def login_did_success(self):
        """
        用户登录成功
        :return:
        """
        self.welcome_user()
        self.save_user()

        #self.get_user_info()

    def welcome_user(self):
        UserLog.print_welcome_user(self)
        pass

    def get_cookie_path(self):
        return Config().USER_DATA_DIR + self.user_name + '.cookie'

    def update_user_info(self, info):
        self.info = {**self.info, **info}

    def get_name(self):
        return self.info.get('user_name', '')

    def save_user(self):
        # self.cluster.set_user_cookie(self.key, self.session.cookies)
        # self.cluster.set_user_info(self.key, self.info)
        with open(self.get_cookie_path(), 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def did_loaded_user(self):
        """
        恢复用户成功
        :return:
        """
        UserLog.add_quick_log(UserLog.MESSAGE_LOADED_USER.format(self.user_name)).flush()
        if self.check_user_is_login() and self.get_user_info():
            UserLog.add_quick_log(UserLog.MESSAGE_LOADED_USER_SUCCESS.format(self.user_name)).flush()
            UserLog.print_welcome_user(self)
        else:
            UserLog.add_quick_log(UserLog.MESSAGE_LOADED_USER_BUT_EXPIRED).flush()

    def user_did_load(self):
        """
        用户已经加载成功
        :return:
        """
        if self.user_loaded: return
        self.user_loaded = True
        # Event().user_loaded({'key': self.key})  # 发布通知

    def get_user_info(self):
        response = self.session.get(API_USER_INFO.get('url'))
        result = response.json()
        user_data = result.get('data.userDTO.loginUserDTO')
        # 子节点访问会导致主节点登录失效 TODO 可快考虑实时同步 cookie
        if user_data:
            self.update_user_info({**user_data, **{'user_name': user_data.get('name')}})
            self.save_user()
            return True
        return False

    def load_user(self):
        cookie_path = self.get_cookie_path()

        if path.exists(cookie_path):
            with open(self.get_cookie_path(), 'rb') as f:
                cookie = pickle.load(f)
                self.cookie = True
                self.session.cookies.update(cookie)
                self.did_loaded_user()
                return True
        return None

    def response_login_check(self, response, **kwargs):
        #if  response.json().get('data.noLogin') == 'true':  # relogin
        if self.check_user_is_login():
            print("No login, then login")
            self.handle_login(expire=True)

    def handle_response(self,response):
        #简单判断如果是302
        if response.status_code == 302:
            logger.info("Not login ,12306 redirect")
            self.handle_login()
            #是否放入缓存
        logger.info("Broswer response %s",response.text)
        return response.json()
    def request_init_dc_page(self):
        """
        请求下单页面 拿到 token
        :return:
        """
        data = {'_json_att': ''}
        response = self.session.post(API_INITDC_URL, data)
        html = response.text
        token = re.search(r'var globalRepeatSubmitToken = \'(.+?)\'', html)
        form = re.search(r'var ticketInfoForPassengerForm *= *(\{.+\})', html)
        order = re.search(r'var orderRequestDTO *= *(\{.+\})', html)
        # 系统忙，请稍后重试
        if html.find('系统忙，请稍后重试') != -1:
            OrderLog.add_quick_log(OrderLog.MESSAGE_REQUEST_INIT_DC_PAGE_FAIL).flush()  # 重试无用，直接跳过
            return False, False, html
        try:
            self.global_repeat_submit_token = token.groups()[0]
            self.ticket_info_for_passenger_form = json.loads(form.groups()[0].replace("'", '"'))
            self.order_request_dto = json.loads(order.groups()[0].replace("'", '"'))
        except:
            return False, False, html  # TODO Error

        slide_val = re.search(r"var if_check_slide_passcode.*='(\d?)'", html)
        is_slide = False
        if slide_val:
            is_slide = int(slide_val[1]) == 1
        return True, is_slide, html

class TicketHandler:
    broswer= ''
    api =''
    retry_time=3
    def __init__(self,broswer) -> None:
        super().__init__()
        # 从redis 获取登录信息
        self.broswer = broswer
        self.api=Request()

    # 登录时把user session 放进去
    # user 信息从数据库查
    # 和线程绑定
    @staticmethod
    def getTicketHandlerInstance(userId):
        # 从redis 获取信息
        ticket_broswer = cacheService.get_ticket_broswer(userId)
        if not ticket_broswer:
            logger.info("No ticket broswer ")
            #设置缓存过期时间，如果用户在登录期间,ticket handler 过期，重新new 的时候，拿不到userInfo,从db 获取,db 没有密码
            #不设置过期时间，如果用户没有退出登录，又很长一段时间没有登录,会有大批无用的key
            info=cacheService.get_user_info(userId)
            if not info:
                info=dbService.getAccount(userId)
                cacheService.set_user_info(userId,info)
            #创建broswer,保存cache
            ticket_broswer=TicketBroswer(info)
            ticket_broswer.login()
            cacheService.set_ticket_broswer(userId,ticket_broswer)
        # else:
        #     logger.info("Get cache ticket broswer")
        #     #缓存存在，检查12306 的登录状态
        #     if not ticket_broswer.check_user_is_login():
        #         logger.info("Cache ticket broswer 12306 login expire ")
        #         ticket_broswer.login()
        #         cacheService.set_ticket_broswer(userId,ticket_broswer)
        ticket_handler=TicketHandler(ticket_broswer)
        return ticket_handler

    def get_user_passengers(self):
        passengers=[]
        pageData={"pageIndex": 1,"pageSize": 10}
        result = self.broswer.post(API_PASSENGER_QUERY,data=pageData)
        logger.info("passengers %s ",result)
        if result.get('data.datas'):
            jsonBody=result.get('data.datas')
            for item in result.get('data.datas'):
                passengers.append({"name": item['passenger_name']})
            return passengers,jsonBody
            # 将乘客写入到文件
            # with open(Config().USER_PASSENGERS_FILE % self.user_name, 'w', encoding='utf-8') as f:
            #     f.write(json.dumps(self.passengers, indent=4, ensure_ascii=False))
        else:
            UserLog.add_quick_log(
                UserLog.MESSAGE_GET_USER_PASSENGERS_FAIL.format(
                    result.get('messages', CommonLog.MESSAGE_RESPONSE_EMPTY_ERROR), self.retry_time)).flush()
            raise BussinessException(500,"Get passengers error")
    def get_passengers_by_members(self, members):
        """
        获取格式化后的乘客信息
        :param members:
        :return:
        [{
            name: '项羽',
            type: 1,
            id_card: 0000000000000000000,
            type_text: '成人',
            enc_str: 'aaaaaa'
        }]
        """
        self.get_user_passengers()
        results = []
        for member in members:
            is_member_code = is_number(member)
            if not is_member_code:
                if member[0] == "*":
                    audlt = 1
                    member = member[1:]
                else:
                    audlt = 0
                child_check = array_dict_find_by_key_value(results, 'name', member)
            if not is_member_code and child_check:
                new_member = child_check.copy()
                new_member['type'] = UserType.CHILD
                new_member['type_text'] = dict_find_key_by_value(UserType.dicts, int(new_member['type']))
            else:
                if is_member_code:
                    passenger = array_dict_find_by_key_value(self.passengers, 'code', member)
                else:
                    passenger = array_dict_find_by_key_value(self.passengers, 'passenger_name', member)
                    if audlt:
                        passenger['passenger_type'] = UserType.ADULT
                if not passenger:
                    UserLog.add_quick_log(
                        UserLog.MESSAGE_USER_PASSENGERS_IS_INVALID.format(self.user_name, member)).flush()
                    return False
                new_member = {
                    'name': passenger.get('passenger_name'),
                    'id_card': passenger.get('passenger_id_no'),
                    'id_card_type': passenger.get('passenger_id_type_code'),
                    'mobile': passenger.get('mobile_no'),
                    'type': passenger.get('passenger_type'),
                    'type_text': dict_find_key_by_value(UserType.dicts, int(passenger.get('passenger_type'))),
                    'enc_str': passenger.get('allEncStr')
                }
            results.append(new_member)

        return results
    def query_price(self,param):
      #  print(self.api.cookies)
    #    response=self.broswer.get(API_TICKET_INDEX)
        #这个使用的就是session,会保存cookie,不过要设置为allow_redirects false
        response = self.broswer.get(url=API_QUERY_PRICE,params=param)
        return response
    @staticmethod
    def query_by_date(info):
        """
        通过日期进行查询
        :return:
        """
        api=''
        if isinstance(info,QueryJobGrabbing):
            leftDate = info.left_date
            leftStationCode = info.left_station
            arriveStationCode = info.arrive_station
            trainNum = info.train_number
            api=Request.getInstance(info.id)
            logger.info("Query info %s", info.__dict__)
        else:
            leftDate = info['leftDate']
            leftStationCode = info['leftStation']
            arriveStationCode = info['arriveStation']
            trainNum = info['trainNum']
            api = Request.getInstance('Internal')
            logger.info("Query info %s", info)
        judge_date_legal(leftDate)
        query_time_out = 5
        api_type = 'leftTicket/query'
        # response = api.get(API_QUERY_INIT_PAGE)
        # if response.status_code == 200:
        #     res = re.search(r'var CLeftTicketUrl = \'(.*)\';', response.text)
        #     try:
        #         api_type = res.group(1)
        #         logger.info("Api type %s",api_type)
        #     except IndexError as error:
        #         print("Error",error)
        #         raise BussinessException(message=error)
        from py12306.helpers.cdn import Cdn
        url = LEFT_TICKETS.get('url').format(left_date=leftDate, left_station=leftStationCode,
                                             arrive_station=arriveStationCode, type=api_type)
        if Config.is_cdn_enabled() and Cdn().is_ready:
            is_cdn = True
            return api.cdn_request(url, timeout=query_time_out, allow_redirects=False)
        is_cdn = False
        response = api.get(url, timeout=query_time_out, allow_redirects=False)
        return handle_response_query_date(response, trainNum)

    def order(self,orderInfo,userId):
        user=cacheService.get_user_info(userId)
        if not user:
            user=dbService.getAccount(userId)
            cacheService.set_user_info(userId,user)
        nameArr,jsonBody=self.get_user_passengers()
        passengersQuery=orderInfo['passengers']
        passengersJson=[]
        #judge_date_legal(orderInfo['left_date'],orderInfo)
        for name in passengersQuery:
            for item in jsonBody:
                if item['passenger_name']== name:
                    passengersJson.append(item)
        orderInfo['passengers']=passengersJson
        current_seat,current_order_seat = self.get_seat(orderInfo['seat'])
        orderInfo['current_seat']=current_seat
        orderInfo['current_order_seat']=current_order_seat
        order=Order(self.broswer,orderInfo,user)
        order.order()

    def get_seat(self, seat):
        current_seat = SeatType.dicts.get(seat)
        current_order_seat = OrderSeatType.dicts.get(seat)
        return current_seat,current_order_seat
    def query_order(self,queryInfo):
        return None

