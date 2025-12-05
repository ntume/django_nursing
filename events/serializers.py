from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Event,EventRSVP,EventMedia

class EventSerializer(serializers.Serializer):
    """serializer for event objects"""
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


class EventModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id','title','description','type','registration','event_date','event_time','location','extra_information','file','created_at','campus','event_date_end','event_time_end')
        read_only_fields = ('id',)
        depth = 1


class EventMediaModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventMedia
        fields = ('id','event','title','type','image','file','created_at')
        read_only_fields = ('id',)


class EventRSVPModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventRSVP
        fields = ('id','event','student','attend','created_at')
        read_only_fields = ('id',)


class EventModelRelationshipSerializer(serializers.ModelSerializer):

    media_files = EventMediaModelSerializer(many = True,read_only=True)

    class Meta:
        model = Event
        fields = ('id','title','description','type','registration','event_date','event_time','location','extra_information','file','created_at','media_files','campus','event_date_end','event_time_end')
        read_only_fields = ('id',)
        depth = 1
