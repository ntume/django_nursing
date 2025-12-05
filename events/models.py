from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from college.models import CollegeCampus
from configurable.models import QuestionType
from students.models import Student
from accounts.models import User
import uuid
import os

def event_file_path(instance, filename):
    """generate file path"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('events/images/',filename)


def event_advert_path(instance, filename):
    """generate file path"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('events/',filename)

# Create your models here.
class EventType(models.Model):

    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type

class EventRegistrationForm(models.Model):

    event_type = models.ForeignKey(EventType,on_delete=models.CASCADE,related_name='registration_forms')
    title = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Event(models.Model):

    CHOICES = (
        ('Yes','Yes'),
        ('No','No'),
    )

    CHOICES_INVITEES = (
        ('1','Students Only'),
        ('2','Company Representatives Only'),
        ('3','Both Students and Company Representatives'),
    )

    title = models.CharField(max_length=50)
    description = models.TextField()
    type = models.ForeignKey(EventType,on_delete=models.SET_NULL,null=True,related_name='events')
    registration = models.CharField(max_length=3,choices=CHOICES)
    event_date = models.DateField()
    event_date_end = models.DateField()
    event_time = models.TimeField()
    event_time_end = models.TimeField()
    location = models.TextField()
    extra_information = models.TextField(null=True,blank=True)
    extra_information_company = models.TextField(null=True,blank=True)
    file = models.FileField(blank=True,upload_to=event_advert_path)
    published = models.CharField(max_length=3)
    invitees = models.CharField(max_length=1,choices=CHOICES_INVITEES)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='events')
    company_organized = models.CharField(max_length=3,choices=CHOICES,default='No')
    registration_form = models.ForeignKey(EventRegistrationForm,on_delete=models.SET_NULL,null=True,related_name='registration_form')
    created_at = models.DateTimeField(auto_now_add=True)
    campus = models.ForeignKey(CollegeCampus,on_delete=models.SET_NULL,null=True,related_name='events')

    def __str__(self):
        return self.title


@receiver(models.signals.pre_save, sender=Event)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file
    except sender.DoesNotExist:
        return False

    new_file = instance.file
    if old_file:
        if not old_file == new_file:
            if os.path.isfile(old_file.url):
                os.remove(old_file.url)

class EventRSVP(models.Model):

    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name='rsvp_students')
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='rsvp_events')
    attend = models.CharField(max_length=10,default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


class EventMedia(models.Model):

    CHOICES = (
        ('Video Link','Video Link'),
        ('image','image'),
        ('PDF file','PDF file')
    )

    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name='media_files')
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=10,choices=CHOICES)
    image = models.ImageField(blank=True, upload_to=event_file_path)
    file = models.FileField(blank=True,upload_to=event_file_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class EventCompanyRSVP(models.Model):

    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name='companies')
    paid = models.CharField(max_length=3,default='No')
    approved = models.CharField(max_length=3,default='No')
    registration_form = models.ForeignKey(EventRegistrationForm,on_delete=models.CASCADE,related_name='company_forms',null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EventRegistrationFormQuestion(models.Model):

    choices = (('one','one'),('many','many'))
    required_choices = (('Yes','Yes'),('No','No'))

    question = models.CharField(max_length=250)
    type = models.ForeignKey(QuestionType,on_delete=models.CASCADE,related_name='registration_form_questions')
    choice = models.CharField(max_length=4,choices=choices,blank=True,default='one')
    registration_form = models.ForeignKey(EventRegistrationForm,on_delete=models.CASCADE,related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    required = models.CharField(max_length = 3, choices=required_choices, default = 'Yes')
    question_number = models.PositiveIntegerField(null=True)
    upload_file = models.FileField(blank=True,upload_to=event_file_path,null=True)

    def __str__(self):
        return self.question


class EventRegistrationCompanyAnswers(models.Model):

    registration_form_company = models.ForeignKey(EventCompanyRSVP,on_delete=models.CASCADE,related_name='event_form_answers')
    question = models.ForeignKey(EventRegistrationFormQuestion,on_delete=models.CASCADE,related_name='answers')
    answer = models.CharField(max_length=256)

    def __str__(self):
        return self.answer

class Announcements(models.Model):

    required_choices = (('Yes','Yes'),('No','No'))

    announcement = models.TextField()
    published = models.CharField(max_length=3,choices=required_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='event_announcement')

    def __str__(self):
        return self.announcement


class AttachmentFile(models.Model):
    
    '''
    Model to upload attachment
    '''

    attachment = models.FileField(upload_to=event_file_path,null=True)
    subject = models.TextField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        self.attachment.delete()
        super().delete(*args, **kwargs)