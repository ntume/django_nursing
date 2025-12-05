from django.db import models
from accounts.models import User

# Create your models here.
class IssueTracker(models.Model):

    '''
    Issue tracker class
    '''

    CHOICES = (
        ('Closed','Closed'),
        ('Open','Open'),
        ('Suspended','Suspended'),
    )

    CHOICES_TYPES = (
        ('Request','Request'),
        ('Issue','Issue'),
        ('Comment','Comment'),
        ('Experience','Experience'),
    )


    description = models.TextField()
    status = models.CharField(choices=CHOICES, max_length=10, default='Open')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True,related_name='issues')
    type = models.CharField(choices=CHOICES_TYPES,max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


class IssueTrackerComments(models.Model):

    '''
    Issue tracker comments
    '''

    comment = models.TextField()
    issuetracker = models.ForeignKey(IssueTracker,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True,related_name='issue_comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment
