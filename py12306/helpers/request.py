import requests
from requests.exceptions import *
from py12306.helpers.api import *
from py12306.helpers.func import *
import re
from py12306.exceptions.BussinessException import BussinessException
from requests_html import HTMLSession, HTMLResponse
from py12306.helpers.api import API_TICKET_INDEX,API_GET_BROWSER_DEVICE_ID
#request.packages.urllib3.disable_warnings()
from py12306.helpers.cache_service import CacheService
from py12306.logging_factory import getLogger
logger=getLogger(__name__)
cacheService=CacheService()
#使用连接池优化,工厂模式
#event green
class Request(HTMLSession):
    """
    请求处理类
    """
    def __init__(self):
        super(Request, self).__init__()
        #封装cookie
        # session=requests.sessions.session()
        # response=session.get(API_TICKET_INDEX)
        # cookies=response.cookies
        # self.cookies=cookies
        # self.get_request_id(session)
    # init 时候处理cookie

    def handle_response(self, response):
        print(response.json())
        return response.json()
    def save_to_file(self, url, path):
        response = self.get(url, stream=True)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        return response
    @staticmethod
    def getInstance(jobId):
        api=cacheService.get_api_request(jobId)
        if not api:
            api=Request()
            response = api.get(API_QUERY_INIT_PAGE)
            if response.status_code == 200:
                res = re.search(r'var CLeftTicketUrl = \'(.*)\';', response.text)
                try:
                    api_type = res.group(1)
                    logger.info("Api type %s", api_type)
                    #应该是自动的
                    #api.cookies.update(response.cookies)
                except IndexError as error:
                    print("Error", error)
                    raise BussinessException(message=error)
            cacheService.set_api_request(jobId,api)
        proxy=cacheService.get_useful_proxy()
        api.proxies=proxy
        logger.info("Use Proxy %s" ,proxy)
        return api
    @staticmethod
    def _handle_response(response, **kwargs) -> HTMLResponse:
        """
        扩充 response
        :param response:
        :param kwargs:
        :return:
        """
        response = HTMLSession._handle_response(response, **kwargs)
        expand_class(response, 'json', Request.json)
        return response

    def add_response_hook(self, hook):
        hooks = self.hooks['response']
        if not isinstance(hooks, list):
            hooks = [hooks]
        hooks.append(hook)
        self.hooks['response'] = hooks
        return self
    def get_request_id(self,session):
        response = session.get(API_GET_BROWSER_DEVICE_ID)
        if response.status_code == 200:
            result = json.loads(response.text)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
            }
            from base64 import b64decode
            session.headers.update(headers)
            response = session.get(b64decode(result['id']).decode())
            if response.text.find('callbackFunction') >= 0:
                result = response.text[18:-2]
            result = json.loads(result)
            session.cookies.update({
                'RAIL_EXPIRATION': result.get('exp'),
                'RAIL_DEVICEID': result.get('dfp'),
            })

    def json(self, default={}):
        """
        重写 json 方法，拦截错误
        :return:
        """
        from py12306.app import Dict
        try:
            result = self.old_json()
            return Dict(result)
        except:
            return Dict(default)

    def request(self, *args, **kwargs):  # 拦截所有错误
        try:
            if not 'timeout' in kwargs:
                from py12306.config import Config
                kwargs['timeout'] = Config().TIME_OUT_OF_REQUEST
            response = super().request(*args, **kwargs)
            return response
        except RequestException as e:
            from py12306.log.common_log import CommonLog
            if e.response:
                response = e.response
            else:
                response = HTMLResponse(HTMLSession)
                # response.status_code = 500
                expand_class(response, 'json', Request.json)
            response.reason = response.reason if response.reason else CommonLog.MESSAGE_RESPONSE_EMPTY_ERROR
            return response

    def cdn_request(self, url: str, cdn=None, method='GET', **kwargs):
        from py12306.helpers.api import HOST_URL_OF_12306
        from py12306.helpers.cdn import Cdn
        if not cdn: cdn = Cdn.get_cdn()
        url = url.replace(HOST_URL_OF_12306, cdn)

        return self.request(method, url, headers={'Host': HOST_URL_OF_12306}, verify=False, **kwargs)

    def dump_cookies(self):
        cookies = []
        for _, item in self.cookies._cookies.items():
            for _, urls in item.items():
                for _, cookie in urls.items():
                    from http.cookiejar import Cookie
                    assert isinstance(cookie, Cookie)
                    if cookie.domain:
                        cookies.append({
                            'name': cookie.name,
                            'value': cookie.value,
                            'url': 'https://' + cookie.domain + cookie.path,
                        })
        return cookies
if __name__ == '__main__':
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
        # 'Cookie': 'JSESSIONID=E68408D1D267F9691F47ACEB16D2798A; RAIL_DEVICEID=A386EaWTlkcTuFZ2Zl_-ACs4Nd7BRN-eN0MIm1nvxxloqOSrzdggfusXfrPt-LQGuZVS9YvATGerYMpoKD2qcqbWmPKAknu0xwKIkSKs2f5b0W6e8o_gdhpMkF4GT493_loFgL3N23TBCygb8TU0tH3Dls6VsQ4m; RAIL_EXPIRATION=1589958850447; BIGipServerotn=267387402.38945.0000; '
        #           'BIGipServerpool_passport=250413578.50215.0000; route=495c805987d0f5c8c84b14f60212447d'
    }
    # 1.代码登录
    index_url = 'https://kyfw.12306.cn/otn/resources/login.html'
    # 2.登录成功之后带着有效的cookie访问请求数据
    # login_response = requests.post(login_url, data=login_form_data)
    # 这个session跟服务器的session不是一回事,这个session可以自动保存cookie,
    # 可以理解为cookiejar
    session = requests.sessions.session()
    login_response = session.get(index_url,headers=headers)
    cookies=login_response.cookies
    print(requests.utils.dict_from_cookiejar(cookies))
    # 个人中心页面
    # requests.utils.add_dict_to_cookiejar(session.cookies,
    #                         {
    #                         'Cookie': 'RAIL_EXPIRATION = 1589917628677; \
    #                         RAIL_DEVICEID = OqzddgfwTu6lFx8ydFTxQ5CrDr3neL - UVO_JoBlOuIfJAtskcDuxq9Um9kiss - 6U \
    #                         aldlw2sPDbTCQfQxuAHQl7aQLAETLn3wvb5k5a4j54XLCe2if5MZpNbrtZ2o0T23u4EJa1_AbZDjffO4rxCkGOAkF0fXyign; \
    #                         BIGipServerpool_statistics = 736166410.44582.0000'
    #                         }
    #                        )
    price_url = "https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=770000T2380A&from_station_no=13&to_station_no=18&seat_types=4311&train_date=2020-05-19"
    # 登录成功  则 访问个人中心页面  session中携带了cookies
    data = session.get(price_url, headers=headers,cookies=cookies,allow_redirects=False)
    print(data)