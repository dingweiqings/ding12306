import requests
from requests.exceptions import *

from py12306.helpers.func import *
from requests_html import HTMLSession, HTMLResponse
from py12306.helpers.cache_service import CacheService
from py12306.helpers.api import API_TICKET_INDEX
requests.packages.urllib3.disable_warnings()
cacheService=CacheService()
#使用连接池优化,工厂模式
class Request(HTMLSession):
    """
    请求处理类
    """

    def __init__(self, userId):
        self.cache=CacheService()
        #缓存没有
        cookies=self.cache.get_cookie(userId)
        if not cookies:
            response=self.get(API_TICKET_INDEX)
            cookies=response.cookies
            self.cache.save_cookie(cookies)
        self.cookies=cookies
    # init 时候处理cookie

    def handle_response(self, response):
        #print(response.history[0].url)
        return response.json()
    def save_to_file(self, url, path):
        response = self.get(url, stream=True)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        return response

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
        'Cookie': 'RAIL_EXPIRATION = 1589917628677; \
    RAIL_DEVICEID = OqzddgfwTu6lFx8ydFTxQ5CrDr3neL - UVO_JoBlOuIfJAtskcDuxq9Um9kiss - 6U \
    aldlw2sPDbTCQfQxuAHQl7aQLAETLn3wvb5k5a4j54XLCe2if5MZpNbrtZ2o0T23u4EJa1_AbZDjffO4rxCkGOAkF0fXyign; \
    BIGipServerpool_statistics = 736166410.44582.0000'
    }
    # 1.代码登录
    index_url = 'https://www.12306.cn/index/'
    # 2.登录成功之后带着有效的cookie访问请求数据
    # login_response = requests.post(login_url, data=login_form_data)
    # 这个session跟服务器的session不是一回事,这个session可以自动保存cookie,
    # 可以理解为cookiejar
    session = requests.sessions.Session()
    login_response = session.get(index_url,headers=headers)
    cookies=login_response.cookies
    print(dict(cookies))
    # 个人中心页面
    # requests.utils.add_dict_to_cookiejar(session.cookies,
    #                         {
    #                         'Cookie': 'RAIL_EXPIRATION = 1589917628677; \
    #                         RAIL_DEVICEID = OqzddgfwTu6lFx8ydFTxQ5CrDr3neL - UVO_JoBlOuIfJAtskcDuxq9Um9kiss - 6U \
    #                         aldlw2sPDbTCQfQxuAHQl7aQLAETLn3wvb5k5a4j54XLCe2if5MZpNbrtZ2o0T23u4EJa1_AbZDjffO4rxCkGOAkF0fXyign; \
    #                         BIGipServerpool_statistics = 736166410.44582.0000'
    #                         }
    #                        )
    price_url = "https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=770000T2380A&from_station_no=13&to_station_no=18&seat_types=4311&train_date=2020-05-18"
    # 登录成功  则 访问个人中心页面  session中携带了cookies
    data = session.get(price_url, headers=headers,allow_redirects=False)
    print(data)