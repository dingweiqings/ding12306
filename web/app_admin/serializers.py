from app_admin.models import WaitUser,QueryJob
from rest_framework import serializers


class WaitUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitUser
        fields = ['id', 'name', 'left_date', 'left_station', 'passengers',
                  'allow_less_member','seats','train_number','arrive_station','state',
                  'createtime', 'updatetime','creater','updater','result','reason']
class QueryJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryJob
        fields = ['id', 'name', 'left_date', 'left_station','train_number','arrive_station','state',
                  'createtime', 'updatetime','creater','updater']
