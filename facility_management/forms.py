from django import forms
from .models import *


class ActivityForm(forms.ModelForm):

    class Meta():
        model = Activity
        fields = ('activity','description',)
        
        
class FacilityForm(forms.ModelForm):

    class Meta():
        model = Facility
        fields = ('facility','location','capacity',)
        
class FacilityActivityBookingForm(forms.ModelForm):

    class Meta():
        model = FacilityActivityBooking
        fields = ('booking_date','booking_time_start','booking_time_end','booking_description')