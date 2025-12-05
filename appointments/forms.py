from django import forms
from .models import Appointment,AppointmentCategory,AppointmentOutcome,AppointmentRecommendation,AppointmentContact

class AppointmentForm(forms.ModelForm):

    class Meta():
        model = Appointment
        fields = ('title',
                  'description',
                  'appointment_date',
                  'appointment_time_start',
                  'appointment_time_end',
                  )
        
        
class AppointmentFileForm(forms.ModelForm):

    class Meta():
        model = Appointment
        fields = ('file',
                  )


class AppointmentCategoryForm(forms.ModelForm):

    class Meta():
        model = AppointmentCategory
        fields = ('category',)


class AppointmentContactForm(forms.ModelForm):

    class Meta():
        model = AppointmentContact
        fields = ('contact',)


class AppointmentRecommendationForm(forms.ModelForm):

    class Meta():
        model = AppointmentRecommendation
        fields = ('recommendation',)


class AppointmentOutcomeForm(forms.ModelForm):

    class Meta():
        model = AppointmentOutcome
        fields = ('priority',)