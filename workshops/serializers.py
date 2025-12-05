from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import WorkshopRSVP,Workshop,WorkshopType

class WorkshopSerializer(serializers.Serializer):
    """serializer for Workshop objects"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    faculty = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()
    registration = serializers.CharField()
    event_date = serializers.CharField()
    event_time = serializers.CharField()
    location = serializers.CharField()
    extra_information = serializers.CharField()
    file = serializers.CharField()
    created_at = serializers.CharField()


class WorkshopModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workshop
        fields = ('id','title','description','type','registration','workshop_date','workshop_enddate','workshop_time','location','extra_information','file','created_at','campus')
        read_only_fields = ('id',)
        depth = 1


class WorkshopRSVPModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkshopRSVP
        fields = ('id','workshop','student','attended','created_at')
        read_only_fields = ('id',)


class WorkshopTypeModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkshopType
        fields = ('id','type')
        read_only_fields = ('id',)
