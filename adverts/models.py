from django.db import models
from django.urls import reverse
from configurable.models import Province
from students.models import Student
from accounts.models import User

import uuid
import os

def update_file_path(instance, filename):
    """generate file path"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('adverts/',filename)


class Type(models.Model):

    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class TypePrices(models.Model):

    type = models.ForeignKey(Type,on_delete=models.CASCADE,related_name='prices')
    period = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='type_prices')
    created_at = models.DateTimeField(auto_now_add=True)



class Advert(models.Model):

    CONTRACT_CHOICES = (
        ('Full-Time','Full-Time'),
        ('Part-Time','Part-Time'),
        ('Work Remotely','Work Remotely'),
    )

    PAID_CHOICES = (
        ('Paid','Paid'),
        ('Unpaid','Unpaid'),
    )

    CHOICES = (('Yes','Yes'),('No','No'))

    company_name = models.CharField(max_length=50,blank=True)
    position = models.CharField(max_length=50)
    description = models.TextField()
    type = models.ForeignKey(Type,on_delete=models.SET_NULL,null=True,related_name='adverts')
    type_price = models.ForeignKey(TypePrices,on_delete=models.SET_NULL,null=True,related_name='adverts')
    paid = models.CharField(max_length=10,choices=PAID_CHOICES)
    requirements = models.TextField()
    apply = models.TextField()
    link = models.TextField(null=True)
    region = models.ForeignKey(Province,on_delete=models.SET_NULL,null=True,related_name='adverts')
    address = models.TextField()
    contract = models.CharField(max_length=20,choices=CONTRACT_CHOICES)
    publish = models.CharField(max_length=3,default='No',choices=CHOICES)
    file = models.FileField(upload_to=update_file_path,default='')
    cut_off_date = models.DateField(null=True)
    post_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='adverts')
    documents = models.TextField(null=True,blank=True)

    def get_absolute_url(self):
        return reverse('wil:advert_list', args=[self.id])

    def __str__(self):
        return self.position


class Selection(models.Model):

    advert = models.ForeignKey(Advert,on_delete=models.CASCADE,related_name='selected_students')
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='selected_adverts')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='selected_advert_students',null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Favourite(models.Model):

    advert = models.ForeignKey(Advert,on_delete=models.CASCADE,related_name='students_favourite')
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='favourite_adverts')
    status = models.CharField(max_length = 10,default='Pending')
    message = models.TextField(default='None')
    created_at = models.DateTimeField(auto_now_add=True)

class Announcements(models.Model):

    required_choices = (('Yes','Yes'),('No','No'))

    announcement = models.TextField()
    published = models.CharField(max_length=3,choices=required_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='advert_announcement')

    def __str__(self):
        return self.announcement
