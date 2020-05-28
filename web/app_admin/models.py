from django.db import models
import uuid
from web.libs.mixins import ModelMixin
from django.contrib.auth.models import AbstractUser
import datetime
from django.utils import timezone
from enum import Enum
# Create your models here.
#  {
#         # 'job_name':  'bj -> sz',  # 任务名称，不填默认会以车站名命名，不可重复
#         'account_key': 0,  # 将会使用指定账号下单
#         'left_dates': [  # 出发日期 :Array
#             "2020-05-02"
#         ],
#         'stations': {  # 车站 支持多个车站同时查询  :Dict or :List
#             'left': '合肥',
#             'arrive': '苏州',
#         },
#         #  # 多个车站示例  (建议添加多个，有时多买几站成功率会高一点)
#         # 'stations': [{
#         #     'left': '北京',
#         #     'arrive': '深圳',
#         # },{  # 多个车站示例
#         #     'left': '北京',
#         #     'arrive': '广州',
#         # }],
#         'members': [  # 乘客姓名，会根据当前账号自动识别乘客类型 购买儿童票 设置两个相同的姓名即可，程序会自动识别 如  ['张三', '张三']
#             "丁为庆",
#             #"*王五", #在姓名前加*表示学生购买成人票
#             # 7,  # 支持通过序号确定唯一乘客，序号查看可通过  python main.py -t 登录成功之后在 runtime/user/ 下找到对应的 用户名_passengers.json 文件，找到对应的 code 填入
#         ],
#         'allow_less_member': 0,  # 是否允许余票不足时提交部分乘客
#         'seats': [  # 筛选座位  有先后顺序 :Array
#             # 可用值: 特等座, 商务座, 一等座, 二等座, 软卧, 硬卧, 动卧, 软座, 硬座, 无座
#             '二等座',
#             '硬座',
#             '硬卧',
#         ],
#         'train_numbers': [  # 筛选车次 可以为空，为空则所有车次都可以提交 如 [] 注意大小写需要保持一致
#         'G7250'
#         ],
#         'except_train_numbers': [  # 筛选车次，排除车次  train_numbers 和 except_train_numbers 不可同时存在
#         ],
#         'period': {  # 筛选时间
#             'from': '00:00',
#             'to': '24:00'
#         }

#     },

STATE_CHOICES=((0, 'NEW'),(1, 'START'), (2,'RUNNING'), (3,'BLOCK'), (4,'END'))
WAIT_STATE_CHOICES=((0,'RUNNING'),(1,'END'))
class WaitUserState(Enum):
       RUNNING=2
       END=4
class QueryJobState(Enum):
       NEW=0
       START= 1
       RUNNING=2
       BLOCK=3
       END=4
class QueryJob(models.Model,ModelMixin):
        id=models.CharField(primary_key=True, max_length=36, auto_created=True, default=uuid.uuid4, editable=False)
        left_date=models.DateField()
        left_station=models.CharField(max_length=100,default='')#以-分割，多组以分号分割
        arrive_station=models.CharField(max_length=100)#以-分割，多组以分号分割
        train_number=models.CharField(max_length=50,null=True,blank=True)
        createtime=models.DateTimeField(default=timezone.now)
        creater = models.CharField(max_length=36,default='')
        updatetime=models.DateTimeField(auto_now=True)
        updater=models.CharField(max_length=36, default='')
        state=models.IntegerField(default=0,choices=STATE_CHOICES)
        count=models.BigIntegerField(default=0)
class Account(AbstractUser,ModelMixin):
        id= models.CharField(primary_key=True, max_length=36, auto_created=True, default=uuid.uuid4, editable=False)
        name = models.CharField(max_length=50)
        mobile = models.CharField(max_length=11,default='')
        createtime=models.DateTimeField(default=timezone.now)
        creater = models.CharField(max_length=36,default='')
        updatetime=models.DateTimeField(auto_now=True)
        updater=models.CharField(max_length=36, default='')
        # username=models.CharField(max_length=50)
        # password=models.CharField(max_length=50)
        password_ticket=models.CharField(max_length=250,default='')
class WaitUser(models.Model,ModelMixin):
        id=models.CharField(primary_key=True, max_length=36, auto_created=True, default=uuid.uuid4, editable=False)
        job_key = models.CharField(max_length=36)
        account_key=models.CharField(max_length=36)
        order=models.IntegerField(default=-1)
        passengers=models.CharField(max_length=256,default='')
        allow_less_member=models.BooleanField(default=False)
        seats=models.CharField(max_length=50,default='')
        createtime=models.DateTimeField(default=timezone.now)
        creater = models.CharField(max_length=36,default='')
        updatetime=models.DateTimeField(auto_now=True)
        updater=models.CharField(max_length=36, default='')

        state=models.IntegerField(default=0,choices=WAIT_STATE_CHOICES)
        name = models.CharField(max_length=100, default='')
        left_date=models.DateField(default=timezone.now)
        left_station=models.CharField(max_length=100,default='')#以-分割，多组以分号分割
        arrive_station=models.CharField(max_length=100, default='')#以-分割，多组以分号分割
        train_number=models.CharField(max_length=50,null=True,blank=True)
        createtime=models.DateTimeField(default=timezone.now)