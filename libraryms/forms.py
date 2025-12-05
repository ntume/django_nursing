from django import forms
from .models import *


class AuthorForm(forms.ModelForm):

    class Meta():
        model = Author
        fields = ('first_name','last_name',)


class CategoryForm(forms.ModelForm):

    class Meta():
        model = Category
        fields = ('category','dewey_code','description')


class BookForm(forms.ModelForm):

    class Meta():
        model = Book
        fields = ('title','reserver_days','borrow_days','is_lendable')
        
        
class BookThumbnailForm(forms.ModelForm):

    class Meta():
        model = Book
        fields = ('thumbnail',)


class PublisherForm(forms.ModelForm):

    class Meta():
        model = Publisher
        fields = ('name',)


class BookCopyForm(forms.ModelForm):

    class Meta():
        model = BookCopy
        fields = ('year_published','edition')


class CheckOutForm(forms.ModelForm):

    class Meta():
        model = CheckOut
        fields = ('due_date',)


class HoldForm(forms.ModelForm):

    class Meta():
        model = Hold
        fields = ('start',)


class NotificationForm(forms.ModelForm):

    class Meta():
        model = Notification
        fields = ('notif_type',)
        
        
class OnlineJournalForm(forms.ModelForm):

    class Meta():
        model = OnlineJournal
        fields = ('title',
                  'url',
                  'publication_type',
                  'access_type',)
        
        
class OnlineJournalThumbnailForm(forms.ModelForm):

    class Meta():
        model = OnlineJournal
        fields = ('thumbnail',)