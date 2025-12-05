from django import forms
from .models import Advert,Type,Announcements,TypePrices

class AdvertCreateForm(forms.ModelForm):

    class Meta():
        model = Advert
        exclude = ['created_at','file','user','company_name','company','cut_off_date','departments','publish','documents','level','degree','type_price','post_date','link']

class MentorAdvertCreateForm(forms.ModelForm):

    class Meta():
        model = Advert
        exclude = ['created_at','file','user','company_name','company','cut_off_date','departments','publish','documents','level','degree','type_price','post_date','link']


class AdvertDocumentForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ('file',)

class AdvertTypeForm(forms.ModelForm):

    class Meta():
        model = Type
        fields = ('type',)

class AnnouncementsForm(forms.ModelForm):

    class Meta():
        model = Announcements
        fields = ('announcement',)


class TypePricesForm(forms.ModelForm):

    class Meta():
        model = TypePrices
        fields = ('period','price',)
