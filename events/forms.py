from django import forms
from .models import Event, EventType, EventMedia, EventRegistrationForm, EventRegistrationFormQuestion,Announcements,AttachmentFile

class EventCreateForm(forms.ModelForm):

    class Meta():
        model = Event
        exclude = ['created_at','user','file','faculties','company','registration_form','campus','extra_information','extra_information_company']

class EventDocumentForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('file',)

class EventTypeForm(forms.ModelForm):

    class Meta():
        model = EventType
        fields = ('type',)

class EventMediaImage(forms.ModelForm):

    class Meta():
        model = EventMedia
        fields = ('type','title','image')

class EventMediaFile(forms.ModelForm):

    class Meta():
        model = EventMedia
        fields = ('type','title','file')


class EventRegistrationFormForm(forms.ModelForm):

    class Meta():
        model = EventRegistrationForm
        fields = ('description','title')


class EventRegistrationFormQuestionForm(forms.ModelForm):

    class Meta():
        model = EventRegistrationFormQuestion
        fields = ('question','choice','required')


class EventRegistrationFormFileQuestionForm(forms.ModelForm):

    class Meta():
        model = EventRegistrationFormQuestion
        fields = ('upload_file',)


class AnnouncementsForm(forms.ModelForm):

    class Meta():
        model = Announcements
        fields = ('announcement',)


class AttachmentFileForm(forms.ModelForm):
    
    class Meta():
        model = AttachmentFile
        fields = ('subject','message',)


class AttachmentFileFileForm(forms.ModelForm):
    
    class Meta():
        model = AttachmentFile
        fields = ('attachment',)