from django.db import models
from django.core.exceptions import ValidationError

from accounts.models import Role, User
from college.models import Staff

# Create your models here.
class Activity(models.Model):
    '''
    Facility activities
    '''
    
    activity = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    
    
class Facility(models.Model):
    '''
    Facilities
    '''
    
    facility = models.CharField(max_length=200)
    location = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='added_facilities')
    activities = models.ManyToManyField(Activity,related_name='facilities',through='FacilityActivity')
    admins = models.ManyToManyField(User,related_name='facility_administrator')
    
class FacilityActivity(models.Model):
    facility = models.ForeignKey('Facility', on_delete=models.CASCADE)
    activity = models.ForeignKey('Activity', on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    
    
class FacilityActivityBooking(models.Model):
    '''
    Booking of facility
    '''
    facility_activity = models.ForeignKey(FacilityActivity, on_delete=models.CASCADE,related_name='bookings')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL,null=True,related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,related_name='bookings')
    booking_date = models.DateField()
    booking_time_start = models.TimeField()
    booking_time_end = models.TimeField(null=True,blank=True)    
    number_of_slots = models.PositiveIntegerField()
    booking_description = models.TextField()
    status = models.CharField(max_length=10,default='Requested')
    status_reason = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    _skip_capacity_validation = False  # default to False
    
    '''def clean(self):
        if self._skip_capacity_validation:
            return  # Skip validation
        
        if self.booking_time_end and self.booking_time_end <= self.booking_time_start:
            raise ValidationError("End time must be after start time.")

        overlapping = FacilityActivityBooking.objects.filter(
            facility_activity=self.facility_activity,
            booking_date=self.booking_date,
            booking_time_start__lt=self.booking_time_end,
            booking_time_end__gt=self.booking_time_start,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        used_slots = sum(b.number_of_slots for b in overlapping)
        available = self.facility_activity.capacity - used_slots

        if self.number_of_slots > available:
            raise ValidationError(f"Only {available} slot(s) are available at that time.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation
        super().save(*args, **kwargs)'''