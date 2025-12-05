from django import forms
from .models import Workshop,WorkshopType

class WorkshopCreateForm(forms.ModelForm):

    class Meta():
        model = Workshop
        exclude = ['created_at','user','file','faculties']

class WorkshopDocumentForm(forms.ModelForm):

    class Meta:
        model = Workshop
        fields = ('file',)

class WorkshopTypeForm(forms.ModelForm):

    class Meta():
        model = WorkshopType
        fields = ('type',)
