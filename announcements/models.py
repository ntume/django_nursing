from django.db import models
from accounts.models import Role, User
from college.models import LearningProgramme, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod

# Create your models here.
class AnnouncementCategory(models.Model):
    '''
    Announcement category class
    '''

    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category
    


class Announcement(models.Model):
    '''
    Annoucement class
    '''

    class Meta:
        ordering = ['-start_date'] 


    title = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    category = models.ForeignKey(AnnouncementCategory,on_delete=models.SET_NULL, null=True,blank=True, related_name='announcements')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='announcements',null=True,blank=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='announcements')
    
    def __str__(self):
        return self.title
    

class LearningProgrammeCohortAnnouncement(models.Model):
    '''
    LP Announcements
    '''

    class Meta:
        ordering = ['-start_date'] 


    title = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    category = models.ForeignKey(AnnouncementCategory,on_delete=models.SET_NULL, null=True,blank=True, related_name='announcements_lp')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='announcements_lp',null=True,blank=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='announcements_lp')
    learning_programme_cohort = models.ForeignKey(LearningProgrammeCohort,on_delete=models.SET_NULL,null=True,related_name='announcements')
    
    def __str__(self):
        return self.title
    


class LearningProgrammeCohortRegisteredAnnouncement(models.Model):
    '''
    Cohort Announcements
    '''

    class Meta:
        ordering = ['-start_date'] 


    title = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    category = models.ForeignKey(AnnouncementCategory,on_delete=models.SET_NULL, null=True,blank=True, related_name='announcements_cohort')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='announcements_cohort',null=True,blank=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='announcements_cohort')
    learning_programme_cohort_registration = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='announcements')
    
    def __str__(self):
        return self.title

