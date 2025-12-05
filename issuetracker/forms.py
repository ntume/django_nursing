from django import forms
from .models import IssueTracker,IssueTrackerComments

class IssueTrackerForm(forms.ModelForm):

    class Meta():
        model = IssueTracker
        exclude = ['created_at','user','status']

class IssueTrackerCommentsForm(forms.ModelForm):

    class Meta():
        model = IssueTrackerComments
        fields = ('comment',)
