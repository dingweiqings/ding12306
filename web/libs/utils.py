# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the MIT License.
from django.http.response import HttpResponse
from django.db.models import QuerySet
from datetime import datetime, date as datetime_date
from decimal import Decimal
import string
import random
import json
import uuid
from rest_framework import exceptions, status
from django.http import Http404
from django.core.exceptions import PermissionDenied
from py12306.exceptions.BussinessException import BussinessException
def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc,BussinessException):
        return json_response(code=500,data=None,message=exc.message)

    return None

def getUserId(request):
    return request.user.id

class DateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, datetime.date):  
            return obj.strftime("%Y-%m-%d")  
        else:  
            return json.JSONEncoder.default(self, obj)
# 转换时间格式到字符串
def human_datetime(date=None):
    if date:
        assert isinstance(date, datetime)
    else:
        date = datetime.now()
    return date.strftime('%Y-%m-%d %H:%M:%S')


# 转换时间格式到字符串(天)
def human_date(date=None):
    if date:
        assert isinstance(date, datetime)
    else:
        date = datetime.now()
    return date.strftime('%Y-%m-%d')


def human_time(date=None):
    if date:
        assert isinstance(date, datetime)
    else:
        date = datetime.now()
    return date.strftime('%H:%M:%S')


# 解析时间类型的数据
def parse_time(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        if len(value) == 10:
            return datetime.strptime(value, '%Y-%m-%d')
        elif len(value) == 19:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    raise TypeError('Expect a datetime.datetime value')


# 传两个时间得到一个时间差
def human_diff_time(time1, time2):
    time1 = parse_time(time1)
    time2 = parse_time(time2)
    delta = time1 - time2 if time1 > time2 else time2 - time1
    if delta.seconds < 60:
        text = '%d秒' % delta.seconds
    elif delta.seconds < 3600:
        text = '%d分' % (delta.seconds / 60)
    else:
        text = '%d小时' % (delta.seconds / 3600)
    return '%d天%s' % (delta.days, text) if delta.days else text


def json_response(code=200, data='',  message='SUCCESS'):
    content = AttrDict(code=code,data=data, message=message)
    if code >= 400:
        content.data = ''
        return HttpResponse(status=code, content=json.dumps(content), content_type='application/json')
    elif hasattr(data, 'to_dict'):
        content.data = data.to_dict()
    elif isinstance(data, (list, QuerySet)) and all([hasattr(item, 'to_dict') for item in data]):
        content.data = [item.to_dict() for item in data]
    return HttpResponse(json.dumps(content, cls=DateTimeEncoder, ensure_ascii=False), content_type='application/json')


# 继承自dict，实现可以通过.来操作元素
class AttrDict(dict):
    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __delattr__(self, item):
        self.__delitem__(item)


# 日期json序列化
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime_date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, Decimal):
            return float(o)
        elif isinstance(o,uuid.UUID):
            return str(o)
        return json.JSONEncoder.default(self, o)


# 生成指定长度的随机数
def generate_random_str(length: int = 4, is_digits: bool = True) -> str:
    words = string.digits if is_digits else string.ascii_letters + string.digits
    return ''.join(random.sample(words, length))

