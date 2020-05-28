from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
from py12306.dto import *
# 消息中间件，密码是你redis的密码
# broker='redis://:123456@127.0.0.1:6379/2' 密码123456
broker = 'redis://10.10.10.201:6379/0'  # 无密码
# 任务结果存储
backend = 'redis://10.10.10.201:6379/1'

# 生成celery对象，'task'相当于key，用于区分celery对象
# include参数需要指定任务模块, cerely 会扫描其中@app.task 的注解
#指定集群计算的任务
app = Celery('addTask', broker=broker, backend=backend,  include=['task.JobTest','task.grabbing'])
# 时区
app.conf.timezone = 'Asia/Shanghai'
# 是否使用UTC
app.conf.enable_utc = False
# celery消息的序列化方式，由于要把对象当做参数所以使用pickle
CELERY_RESULT_SERIALIZER = ['pickle']
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
#配置序列化方式
app.conf.task_serializer=CELERY_TASK_SERIALIZER
app.conf.accept_content=CELERY_ACCEPT_CONTENT
app.conf.result_accept_content=CELERY_RESULT_SERIALIZER

# 定时执行
# app.conf.beat_schedule = {
#     # 名字随意命名
#     'add-every-5-seconds': {
#         # 执行add_task下的addy函数
#         'task': 'celery_task.add_task.add',
#         # 每10秒执行一次
#         'schedule': timedelta(seconds=10),
#         # add函数传递的参数
#         'args': (1, 2)
#     },
#     'add-every-10-seconds': {
#         'task': 'celery_task.add_task.add',
#         # crontab不传的参数默认就是每的意思，比如这里是每年每月每日每天每小时的5分执行该任务
#         'schedule': crontab(minute=5),
#         'args': (1, 2)
#     }
# }

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'task.grabbing.push_worker_queue',
        'schedule': 10.0,
        'args': ()
    },
}
