from django.db import models
from accounts.models import User
import os
import uuid

# Create your models here.

class Category(models.Model):

    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category

def update_coverphoto_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('blog/coverimage/',filename)

def update_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('blog/attachments/',filename)

class Blog(models.Model):

    choices_publish = (('Yes','Yes'),('No','No'))
    choices_viewership = (('Public','Public'),('Registered User','Registered User'))

    title = models.CharField(max_length=256)
    short_description = models.CharField(max_length=256)
    article = models.TextField()
    file_attachment = models.FileField(upload_to=update_filename,default='',null=True,blank=True)
    cover_image = models.ImageField(upload_to=update_coverphoto_name,default='',null=True,blank=True)
    link = models.CharField(max_length=255,null=True,blank=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name='blog_entries')
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='blog_entries')
    publish = models.CharField(max_length=3,choices=choices_publish,default='Yes')
    viewership = models.CharField(max_length=20,choices=choices_viewership,default='Public')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):

    choices_publish = (('Yes','Yes'),('No','No'))

    comment = models.TextField()
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,related_name='comments')
    published = models.CharField(max_length=3,choices=choices_publish,default='No')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='blog_comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

def update_image_name(instance, filename):
    path = "blog/images/"
    ext = filename.split('.')[-1]
    format = "{}.{}".format(instance.id,ext)
    return os.path.join(path, format)

class Image(models.Model):

    image = models.ImageField(upload_to=update_image_name)
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,related_name='images')

    def update_image_name(instance, filename):
        path = "blog/images/"
        format = instance.id
        return os.path.join(path, format)
