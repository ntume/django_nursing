from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from .models import AppointmentCategory, AppointmentRecommendation, Appointment, AppointmentUpdate, AppointmentOutcome, AppointmentCallInfo,AppointmentContact

class AppointmentCategoryModelSerializer(serializers.ModelSerializer):
    """Serizliser class for Appointment Category """

    class Meta:
        model = AppointmentCategory
        fields = ('id','category')
        read_only_fields = ('id',)


class AppointmentModelSerializer(serializers.ModelSerializer):
    """Serializer class Appointment"""

    class Meta:
        model = Appointment
        fields = ('id','title','description','appointment_date','appointment_time_start','appointment_time_end','category','status','feedback_student','appointment_acceptance_feedback','created_at','video_call','contact',)
        read_only_fields = ('id','appointment_acceptance_feedback','created_at','status','video_call')


class AppointmentCallInfoModelSerializer(serializers.ModelSerializer):
    """Serializer class Appointment"""

    class Meta:
        model = AppointmentCallInfo
        fields = ('id','room','appt_id','type_of_appointment','token','completed')
        read_only_fields = ('id','room','appt_id','type_of_appointment','token')


class AppointmentUpdateModelSerializer(serializers.ModelSerializer):
    """ serializer class for AppointmentUpdate"""

    class Meta:
        model = AppointmentUpdate
        fields = ('id','appointment','who_updates','message','created_at')
        read_only_fields = ('id','appointment','who_updates','message','created_at')


class AppointmentContactModelSerializer(serializers.ModelSerializer):
    """ serializer class for Appointment Contact"""

    class Meta:
        model = AppointmentContact
        fields = ('id','contact',)
        read_only_fields = ('id','contact',)
