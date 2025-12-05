from django.db import models
from accounts.models import User

# Create your models here.

class Task(models.Model):

    choices_status = (('Completed','Completed'),('Pending','Pending'))

    task = models.CharField(max_length=50,null=False)
    status = models.CharField(max_length=10,choices=choices_status,default='Pending')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
