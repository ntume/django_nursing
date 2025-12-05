import os
import uuid
from django.db import models
from accounts.models import User
from students.models import Student

def update_file_path(instance, filename):
    """generate file path"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('generaldocuments/',filename)

# Create your models here.
class AppointmentCategory(models.Model):
    '''
    Appointment category class
    '''

    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category


class AppointmentRecommendation(models.Model):
    '''
    Appointment Recommendation class
    '''

    recommendation = models.CharField(max_length=256)

    def __str__(self):
        return self.recommendation


class AppointmentContact(models.Model):
    '''
    Appointment Recommendation class
    '''

    contact = models.CharField(max_length=256)

    def __str__(self):
        return self.contact



class Appointment(models.Model):
    '''
    Appointment class
    '''

    CHOICES = (
               ('Pending','Pending'),
               ('Assigned','Assigned'),
               ('Approved','Approved'),
               ('Declined','Declined'),
               ('NewTime','NewTime'),
               ('New Time Accepted','New Time Accepted'),
               ('New Time Rejected','New Time Rejected'),
               ('Completed','Completed'),
           )


    title = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField()
    appointment_date = models.DateField()
    appointment_time_start = models.TimeField()
    appointment_time_end = models.TimeField(null=True,blank=True)
    category = models.ForeignKey(AppointmentCategory,on_delete=models.SET_NULL, null=True,blank=True, related_name='appointments')
    status = models.CharField(max_length=20,choices=CHOICES,default='Pending')
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='appointments')
    assigned = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='assigned_appointments',null=True,blank=True)
    feedback_student = models.TextField(blank=True)
    appointment_acceptance_feedback = models.TextField(blank=True)
    referred_by = models.CharField(max_length = 50,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contact = models.ForeignKey(AppointmentContact,on_delete=models.SET_NULL,related_name='contact_method',null=True,blank=True)
    link = models.TextField(null=True,blank=True)
    file = models.FileField(blank=True,upload_to=update_file_path,null=True)

    def __str__(self):
        return self.title
    
    def get_outcome_summary(self):
        return ', '.join([
            outcome.recommendation.recommendation  # or outcome.recommendation.name, etc.
            for outcome in self.outcome.all()
        ])


class AppointmentUpdate(models.Model):

    '''
    Model to keep track of all appointment changes
    '''

    choices_who = (('staff','staff'),('student','student'))

    appointment = models.ForeignKey(Appointment,on_delete=models.CASCADE,related_name='updates')
    who_updates = models.CharField(max_length=10,choices=choices_who)
    message = models.CharField(max_length= 256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class AppointmentOutcome(models.Model):

    '''
    Model for outcome of appointments
    '''

    appointment = models.ForeignKey(Appointment,on_delete=models.CASCADE,related_name='outcome')
    recommendation = models.ForeignKey(AppointmentRecommendation,on_delete=models.CASCADE,related_name='appointments')
    priority = models.PositiveIntegerField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='outcome')
    created_at = models.DateTimeField(auto_now_add=True)


class AppointmentNotes(models.Model):

    '''
    Model for appointment notes
    '''

    appointment = models.ForeignKey(Appointment,on_delete=models.CASCADE,related_name='notes')
    notes = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='appointment_notes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.notes