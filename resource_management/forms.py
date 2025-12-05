from django import forms
from .models import *
      
        
class ResourceForm(forms.ModelForm):

    class Meta():
        model = Resource
        fields = ('resource','description','number_of_resources',)
        
class ResourceBookingForm(forms.ModelForm):

    class Meta():
        model = ResourceBooking
        fields = ('booking_date','booking_time_start','booking_time_end','booking_description','number_of_resources')