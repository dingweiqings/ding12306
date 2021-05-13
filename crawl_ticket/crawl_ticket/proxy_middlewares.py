import requests
import json

class ProxyMiddleware(object):

    def __init__(self) -> None:
        super().__init__()
    def process_request(self, request, spider):
        url='http://10.10.10.76:5010/get'
        response=requests.get(url)
        body=json.loads(response.text)
        request.meta["proxy"] = body['proxy']


if __name__ == '__main__':
    # proxy=ProxyMiddleware()
    # proxy.process_request(None,None)
    url = 'http://10.10.10.76:5010/get'
    response = requests.get(url)
    body = json.loads(response.text)
    print("Use  proxy {}".format(body))