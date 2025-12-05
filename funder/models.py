from django.db import models
from students.models import StudentLearningProgrammeRegistration
from accounts.models import User

# Create your models here.
class Funder(models.Model):

    '''
    Model to save the funders
    '''

    funder = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.funder


class Funding(models.Model):

    '''
    Model to save the funders funding
    '''

    funder = models.ForeignKey(Funder,on_delete=models.CASCADE,related_name='funding')
    amount = models.PositiveIntegerField()
    description = models.TextField()
    start = models.DateField()
    end = models.DateField()
    number_of_students = models.PositiveIntegerField()
    file = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.amount


class FundingStudent(models.Model):

    '''
    Model for student under funding
    '''

    funding = models.ForeignKey(Funding,on_delete=models.CASCADE,related_name = 'students')
    student = models.OneToOneField(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name= 'funding')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.student.surname


class FundingRep(models.Model):

    '''
    Model for funding representatives
    '''

    funder = models.ForeignKey(Funder,on_delete=models.CASCADE,related_name='representatives')
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    cellphone = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='funder_reps',null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.surname
