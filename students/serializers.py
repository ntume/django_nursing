from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Student, Country, Level, Language

class StudentSerializer(serializers.ModelSerializer):
    """Serializer for stduent class"""

    class Meta:
        model = Student
        fields = ('id','student_number','id_number','name','surname','gender','race','disability','disabilityspecify','contact_number','employed','bio','driverslicence','address','language','qualification')

class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country class"""

    class Meta:
        model = Country
        fields = ('id','countryName',)

class LevelSerializer(serializers.ModelSerializer):
    """Serializer for Level class"""

    class Meta:
        model = Level
        fields = ('id','level',)

class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for Level class"""

    class Meta:
        model = Language
        fields = ('id','language',)
