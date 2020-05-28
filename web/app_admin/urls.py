from django.urls import path

from .views import QueryJobView,WaitUserView
from .views import AccountView
from .views import mylogin, myregister,mylogout,citylist,queryticket,order_ticket,query_passengers,query_price


from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'queryjob', QueryJobView, basename='queryjob')
router.register(r'querytask', WaitUserView, basename='querytask')
urlpatterns = [
  #  path('queryjob/', QueryJobView.as_view()),
    path('account/', AccountView.as_view()),
    path('account/login/', mylogin),
    #path('index/', index),
    path('account/register/', myregister),
    path('account/logout/', mylogout),
    path('queryticket/citylist/',citylist),
    path('queryticket/ticket/',queryticket),
    path('queryticket/order/', order_ticket),
    path('queryticket/passengers/', query_passengers),
    path('queryticket/price/', query_price)
]
urlpatterns = urlpatterns + router.urls