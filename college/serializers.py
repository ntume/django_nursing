from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Campus,DegreeChoices



class CampusModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campus
        fields = ('id','campus',)
        read_only_fields = ('id',)


class DegreeChoicesModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DegreeChoices
        fields = ('id','degree','shortcode',)
        read_only_fields = ('id',)
