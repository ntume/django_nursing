from django.db import models
from students.models import Student
from accounts.models import User
from college.models import CollegeCampus
import uuid
import os

def workshop_file_path(instance, filename):
    """generate file path"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('workshops/',filename)

# Create your models here.

class WorkshopType(models.Model):

    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type

class Workshop(models.Model):

    CHOICES = (
        ('Yes','Yes'),
        ('No','No'),
    )

    title = models.CharField(max_length=50)
    description = models.TextField()
    type = models.ForeignKey(WorkshopType,on_delete=models.SET_NULL,null=True,related_name='workshops')
    registration = models.CharField(max_length=3,choices=CHOICES)
    workshop_date = models.DateField()
    workshop_enddate = models.DateField()
    workshop_time = models.TimeField()
    location = models.TextField()
    extra_information = models.TextField()
    file = models.FileField(upload_to=workshop_file_path,default='')
    published = models.CharField(max_length=3,choices=CHOICES)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='workshops')
    created_at = models.DateTimeField(auto_now_add=True)
    campus = models.ForeignKey(CollegeCampus,on_delete=models.SET_NULL,null=True,related_name='workshops')

    def __str__(self):
        return self.title




class WorkshopRSVP(models.Model):

    workshop = models.ForeignKey(Workshop,on_delete=models.CASCADE,related_name='rsvp_students')
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='rsvp_workshops')
    attended = models.CharField(max_length=10,default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.name
