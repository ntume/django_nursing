from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Blog

class BlogSerializer(serializers.Serializer):
    """serializer for blog_view objects"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    short_description = serializers.CharField()
    article = serializers.CharField()
    file_attachment = serializers.CharField()
    cover_image = serializers.CharField()
    link = serializers.CharField()
    category = serializers.CharField()
    author = serializers.CharField()
    created_at = serializers.CharField()


class BlogModelSerializer(serializers.ModelSerializer):
    """Serializer for Blog model"""

    class Meta:
        model = Blog
        fields = ('id','title','short_description','article','file_attachment','cover_image','link','category','created_at')
        read_only_fields = ('id',)
        depth = 1
