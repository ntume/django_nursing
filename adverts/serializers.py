from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Advert,Favourite

class AdvertSerializer(serializers.Serializer):
    """serializer for advert objects"""
    id = serializers.IntegerField()
    company_name = serializers.CharField()
    position = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()
    paid = serializers.CharField()
    requirements = serializers.CharField()
    industry = serializers.CharField()
    apply = serializers.CharField()
    region = serializers.CharField()
    address = serializers.CharField()
    contract = serializers.CharField()
    created_at = serializers.CharField()
    departments = serializers.CharField()


class AdvertModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advert
        fields = ('id','company_name','position','description','type','paid','requirements','industry','apply','region','address','contract','file','created_at','departments')
        depth = 1


class FavouriteModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourite
        fields = ('id','advert','status','message','created_at',)
