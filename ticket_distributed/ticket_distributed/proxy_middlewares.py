import requests
import json
from py12306.helpers.cache_service import CacheService
cacheService=CacheService()
class ProxyMiddleware(object):

    def __init__(self) -> None:
        super().__init__()
    def process_request(self, request, spider):
        url='http://10.10.10.76:5010/get'
        response=requests.get(url)
        body=json.loads(response.text)
        request.meta["proxy"] = body['proxy']
        cookies=cacheService.get_cookie()
       # request.meta['Cookie']=
        print("Add cookies ")
        print(cookies)
        request.cookies=cookies

if __name__ == '__main__':
    # proxy=ProxyMiddleware()
    # proxy.process_request(None,None)
    url = 'http://10.10.10.76:5010/get'
    response = requests.get(url)
    body = json.loads(response.text)
    print("Use  proxy {}".format(body))