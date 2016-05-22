import django_filters
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Roll
from rest_framework import serializers, filters
from accounts.models import Trainee
from schedules.models import Event
from leaveslips.models import IndividualSlip, GroupSlip
from leaveslips.serializers import IndividualSlipSerializer, GroupSlipSerializer
from schedules.serializers import EventSerializer, ScheduleSerializer
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
    ListBulkCreateUpdateDestroyAPIView,
)

class RollSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta(object):
        model = Roll
        list_serializer_class = BulkListSerializer
        fields = ['id','event','trainee','status','finalized','notes','timestamp','submitted_by','date']
    def create(self, validated_data):
    	trainee = validated_data['trainee']
    	event = validated_data['event']
        date = validated_data['date']
        submitted_by = validated_data['submitted_by']

    	# checks if roll exists for given trainee, event, and date
    	roll_override = Roll.objects.filter(trainee=trainee).filter(event=event.id).filter(date=date)
    	# checks if event exists for given event and date
    	event_override = Event.objects.filter(name=event.name).filter(weekday=date.weekday())

        # event and roll exists, so update
        if roll_override and event_override and submitted_by == trainee:
        	roll_override.update(**validated_data)
        	return validated_data
        elif event_override: # no roll, so create roll
        	return Roll.objects.create(**validated_data)
        else: # no event, so don't do anything.
            return validated_data

class RollFilter(filters.FilterSet):
    timestamp__lt = django_filters.DateTimeFilter(name = 'timestamp', lookup_expr = 'lt')
    timestamp__gt = django_filters.DateTimeFilter(name = 'timestamp', lookup_expr = 'gt')
    finalized = django_filters.BooleanFilter()
    class Meta:
        model = Roll
        fields = ['id','status','finalized','notes','timestamp','event','trainee','submitted_by','date']

class AttendanceSerializer(BulkSerializerMixin, ModelSerializer):
    name = SerializerMethodField('get_trainee_name')
    individualslips = IndividualSlipSerializer(many=True,)
    groupslips = GroupSlipSerializer(many=True,)
    rolls = RollSerializer(many=True,)
    class Meta(object):
   		model = Trainee
   		list_serializer_class = BulkListSerializer
   		fields = ['name','individualslips','groupslips','rolls']
    def get_trainee_name(self, obj):
        return obj.__unicode__()

class AttendanceFilter(filters.FilterSet):
	class Meta:
		model = Trainee
		fields = ['id','individualslips','groupslips','rolls','term']