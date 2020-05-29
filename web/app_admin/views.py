from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

# Create your views here.
from django.views import View
from django.views.generic import ListView
from web.libs.utils import json_response,human_datetime, human_time
from web.libs.parser import JsonParser, Argument
from .models import QueryJob,QueryJobState,WaitUser,WaitUserState
from .models import Account
from datetime import date
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import reverse,redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login,authenticate,logout  # authenticate:user认证  login:用户登录并记录session
from web.app_admin.serializers import WaitUserSerializer
from py12306.helpers.TicketHandler import TicketHandler
from rest_framework import viewsets
from task.QueryTaskCls  import Job
from py12306.query.query import Query
from py12306.helpers.station import Station
from py12306.helpers.request import Request
from task.JobTest import JobTest
from rest_framework.response import Response
from py12306.helpers.func import get_param,get_body
import threading
from web.libs.utils import getUserId
from py12306.helpers.cache_service import CacheService
from py12306.helpers.db_service import DbService
from py12306.dto.QueryJob import QueryJobGrabbing
import base64
import datetime
from django.db import connection
from web.logging_factory import getLogger
logger=getLogger(__name__)
dbService=DbService()
# class QueryJobView(View):

#     @method_decorator(login_required)
#     def get(self, request):
#         # <view logic>
#         data=QueryJob.objects.all()
#         return json_response(data)
#     @method_decorator(login_required)
#     def post(self, request):
#         form, error = JsonParser(
#         #    Argument('id', type=int, required=False),
#             Argument('name', type=str, help='缺少必要参数name'),
#           #  Argument('account_key', type=str,help='请输申请标题account'),
#             Argument('left_date', type=date, help='缺少必要参数leftdate',pattern='%Y-%m-%d'),
#             Argument('stations', type=str),
#             Argument('peroid',required=False),
#             Argument('members'),
#             Argument('seats'),
#             Argument('allow_less_member', type=bool),
#             Argument('train_numbers'),
#             Argument('except_train_numbers'),
#         ).parse(request.body)
#         form['account_key'] = request.user.id
#         if error is None:
#                 QueryJob.objects.create(**form)
#         return json_response(message=error)
class QueryJobView(viewsets.ModelViewSet):
    queryset = QueryJob.objects.all().order_by('-createtime')
    serializer_class = WaitUserSerializer
    def patch(self, request, *args, **kwargs):
        params=request.query_params
        self.kwargs=params
        obj=super().update(request,*args,partial=True)
        return obj

class WaitUserView(viewsets.ModelViewSet):
    queryset = WaitUser.objects.all().order_by('-createtime')
    serializer_class = WaitUserSerializer

    def get_queryset(self):
        return super().get_queryset()

    def patch(self, request, *args, **kwargs):
        params=request.query_params
        self.kwargs=params
        return self.update(request, *args, **kwargs)


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request,*args,partial=True)
    def create(self, request, *args, **kwargs):
        #body 中参数已经被rest framework 封装
        grabbingInfo=request.data
        trainNum=grabbingInfo['trainNum']
        leftDate=grabbingInfo['left_date']
        #增加车次,job 可以不加事务
        with transaction.atomic():
            save_id = transaction.savepoint()
            cursor = connection.cursor()
            try:
                for num in trainNum:
                    for left_date in leftDate:
                          dbSet=QueryJob.objects.filter(left_date=left_date,train_number=num,
                                                  left_station=grabbingInfo['left_station'],arrive_station=grabbingInfo['arrive_station']
                                                           )
                          if not len(dbSet):
                              saveObj={}
                              saveObj['left_date']=left_date
                              saveObj['arrive_station']=grabbingInfo['arrive_station']
                              saveObj['left_station']=grabbingInfo['left_station']
                              saveObj['train_number']=num
                              saveObj['creater']=request.user.id
                              saveObj['updater']=request.user.id
                              saveObj['state']=QueryJobState.START.value
                              dbExists=QueryJob.objects.create(**saveObj)
                          else:
                              dbExists = dbSet[0]  # 取到对应object,而不是Queryset
                        #处理wait user,根据order 倒序
                          waitUserset=WaitUser.objects.filter(job_key=dbExists.id,account_key=request.user.id).order_by('-order')
                          #同一个用户，相同车次不重复创建
                              # 创建事务保存点
                          if not len(waitUserset):
                                  waitUserObj = {}
                                  waitUserObj['seats'] = ",".join(grabbingInfo['seat'])
                                  waitUserObj['passengers']=",".join(grabbingInfo['passengers'])
                                  waitUserObj['job_key'] = dbExists.id
                                  waitUserObj['account_key'] = request.user.id
                                  waitUserObj['creater'] = request.user.id
                                  waitUserObj['updater'] = request.user.id
                                  waitUserObj['name']=request.user.username+"-"+str(int(datetime.datetime.now().timestamp()))
                                  waitUserObj['account_key']=request.user.id
                                  waitUserObj['left_date']=left_date
                                  waitUserObj['arrive_station']=grabbingInfo['arrive_station']
                                  waitUserObj['left_station']=grabbingInfo['left_station']
                                  waitUserObj['train_number']=num
                                  saveObj['state'] = WaitUserState.RUNNING.value
                                  waitUser=WaitUser.objects.create(**waitUserObj)
                                  # db = MySQLdb.connect(user='root', db='testdb', passwd='', host='localhost',
                                  #                      charset='utf8')
                                  cursor.execute("UPDATE `app_admin_waituser` a , (SELECT MAX(`order`)+1  AS  md  FROM `app_admin_waituser` where job_key='%s' ) b SET a.order =b.md"
                                                 " WHERE id = '%s'" %(dbExists.id,waitUser.id))
                          else:
                                  waitUser = waitUserset[0]  # 取到对应object,而不是Queryset
                                  waitUserObj={}
                                  waitUserObj['seats']=",".join(grabbingInfo['seat'])
                                  waitUserObj['passengers']=",".join(grabbingInfo['passengers'])
                                  waitUserObj['updater']=  request.user.id
                                  #使用QueryUserSet 更新
                                  waitUserset.update(**waitUserObj)
                transaction.savepoint_commit(save_id)
                cursor.close()
                        #没错则提交
            except Exception as e:
               print("Occur error ",e)
               transaction.savepoint_rollback(save_id)
               return json_response(code=500,message=str(e))
            finally:
                cursor.close()
        return json_response()
class AccountView(View):
    @method_decorator(login_required)
    def get(self, request):
        # <view logic>
        id = request.GET.get('id', default='')
        data= Account.objects.get(pk=id)
        data.access = ['super_admin']
        return json_response(data=data)
def mylogout(request):
    cacheService=CacheService()
    cacheService.del_ticket_handler(getUserId(request))
    cacheService.del_user_info(getUserId(request))
    cacheService.del_ticket_broswer(getUserId(request))
    logout(request)
    return json_response(data=None)
def mylogin(request):
    # if request.method == 'GET':
    #     return render(request, 'login.html')
    if request.method =='POST':
        form, error = JsonParser(
        #    Argument('id', type=int, required=False),
          # Argument('name', type=str),
            Argument('username', type=str),
            Argument('password', type=str),
        ).parse(request.body)
        if error is None:
               user= authenticate(request, **form)
               # 设置session
               if user:
                    login(request, user)
                    cacheService=CacheService()
                    cacheService.set_user_info(user.id, dbService.getAccount(user.id))
                    return json_response(message="SUCCESS", data={'token': user.id})  # 需要加/ ,url 的名字去查找
               else:
                   return json_response(code=400, message="用户名或密码错误")
        return json_response(code=400,message=error)
def myregister(request):
    if request.method =='POST':
        form, error = JsonParser(
        #    Argument('id', type=int, required=False),
           Argument('name', type=str),
            Argument('username', type=str),
            Argument('password', type=str),
            Argument('email', type=str),
            Argument('mobile', type=str),
        ).parse(request.body)
        if error is None:
                form['password_ticket']=base64.b64encode(form['password'])
                form['password']= make_password(form['password'])
                Account.objects.create(**form)
               # return redirect("/index") 需要加/ ,url 的名字去查找
                return json_response(message="创建成功")
        return json_response(code=400,message=error)
@login_required
def citylist(request):
    return json_response(data=Station().stations)
@login_required
def queryticket(request):
    param=get_param(request)
    data=TicketHandler.query_by_date(param)
    return json_response(data=data)
@login_required
def query_passengers(request):
    # handler= UserTicketHandler()
    # handler.getPassengers()
    handler= TicketHandler.getTicketHandlerInstance(getUserId(request))
    data=handler.get_user_passengers()[0]
    return json_response(data=data)
@login_required
def order_ticket(request):
    handler= TicketHandler.getTicketHandlerInstance(getUserId(request))
    orderInfo=get_body(request)
    data=handler.order(orderInfo,getUserId(request))
    return json_response()
@login_required
def query_price(request):
    handler= TicketHandler.getTicketHandlerInstance(getUserId(request))
    param=get_param(request)
    data=handler.query_price(param)
    return json_response(data=data)
@login_required
def query_order(request):
    handler=TicketHandler.getTicketHandlerInstance(getUserId(request))
    param = get_param(request)
    data=handler.query_order(param)
    return json_response(data=data)
