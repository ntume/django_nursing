from django.contrib import admin
from .models import IssueTracker, IssueTrackerComments

# Register your models here.

admin.site.register(IssueTracker)
admin.site.register(IssueTrackerComments)
