from django import forms
from .models import AnnouncementCategory,Announcement, LearningProgrammeCohortAnnouncement, LearningProgrammeCohortRegisteredAnnouncement

class AnnouncementForm(forms.ModelForm):

    class Meta():
        model = Announcement
        fields = ('title',
                  'description',
                  'start_date',
                  'end_date',
                  )


class AnnouncementCategoryForm(forms.ModelForm):

    class Meta():
        model = AnnouncementCategory
        fields = ('category',)



class LearningProgrammeCohortAnnouncementForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeCohortAnnouncement
        fields = ('title',
                  'description',
                  'start_date',
                  'end_date',
                  )
        

class LearningProgrammeCohortRegisteredAnnouncementForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeCohortRegisteredAnnouncement
        fields = ('title',
                  'description',
                  'start_date',
                  'end_date',
                  )