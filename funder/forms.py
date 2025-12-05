from django import forms
from .models import Funder, Funding, FundingRep


class FundingForm(forms.ModelForm):

    class Meta():
        model = Funding
        exclude = ['created_at','funder','faculty','file']


class FunderForm(forms.ModelForm):

    class Meta():
        model = Funder
        exclude = ['logo']
