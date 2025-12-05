from django.db import models
from django.core.exceptions import ValidationError

from accounts.models import Role, User
from college.models import Staff

# Create your models here.
    
    
class Resource(models.Model):
    '''
    Resources
    '''
    
    resource = models.CharField(max_length=200)
    description = models.TextField()
    number_of_resources = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='added_resources')
    admins = models.ManyToManyField(User,related_name='resource_administrator')
    
    
    
class ResourceBooking(models.Model):
    '''
    Booking of resource
    '''
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE,related_name='resource_bookings')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL,null=True,related_name='resource_bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,related_name='resource_bookings')
    booking_date = models.DateField()
    booking_time_start = models.TimeField()
    booking_time_end = models.TimeField(null=True,blank=True)    
    number_of_resources = models.PositiveIntegerField()
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

        overlapping = ResourceBooking.objects.filter(
            resource=self.resource,
            booking_date=self.booking_date,
            booking_time_start__lt=self.booking_time_end,
            booking_time_end__gt=self.booking_time_start,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        used_slots = sum(b.number_of_resources for b in overlapping)
        available = self.resource.number_of_resources - used_slots

        if self.number_of_resources > available:
            raise ValidationError(f"Only {available} slot(s) are available at that time.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation
        super().save(*args, **kwargs)'''