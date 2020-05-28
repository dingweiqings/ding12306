# import os
#
# if __name__ == "celery_task.send_email":
#     # 因为需要用到django中的内容，所以需要配置django环境
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "do_celery.settings")
#     import django
#     django.setup()
#     # 导入celery对象app
#     from .cerely import app
#     # 导入django自带的发送邮件模块
#     from django.core.mail import send_mail
#     import threading
#     from . import settings
#
#     @app.task
#     def send_email1(id):  # 此时可以直接传邮箱，还能减少一次数据库的IO操作
#         # 此处的id由用户注册的视图函数中传入
#         email = 'dingweiqings@163.com'
#         # 启用线程发送邮件，此处最好加线程池
#         t = threading.Thread(target=send_mail, args=(
#             "激活邮件，点击激活账号",  # 邮件标题
#             '点击该邮件激活你的账号，否则无法登陆',  # 给html_message参数传值后，该参数信息失效
#             settings.EMAIL_HOST_USER,  # 用于发送邮件的邮箱地址
#             [email],  # 接收邮件的邮件地址，可以写多个
#             ),
#             # html_message中定义的字符串即HTML格式的信息，可以在一个html文件中写好复制出来放在该字符串中
#             kwargs={'html_message': "<a href='http://127.0.0.1:8000/active_user/?id=%s'>点击激活gogogo</a>" % id}
#         )
#         t.start()