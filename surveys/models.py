from django.db import models
from accounts.models import User
from configurable.models import QuestionType

# Create your models here.

class QuestionType_old(models.Model):

    '''
    The different question types we can ask in all surveys
    '''

    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

class Category(models.Model):

    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category

class Survey(models.Model):

    choices_publish = (('Yes','Yes'),('No','No'))

    role_choices = (
                    (6,'Students'),
                    (3,'Company Representatives'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,related_name='surveys')
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name='surveys')
    published = models.CharField(max_length=3,choices=choices_publish,default='No')
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.PositiveIntegerField(choices = role_choices,default = 6)

    def __str__(self):
        return self.title

class Question(models.Model):

    choices = (('one','one'),('many','many'))

    question = models.CharField(max_length=250)
    type = models.ForeignKey(QuestionType,on_delete=models.CASCADE,related_name='survey_questions')
    choice = models.CharField(max_length=4,choices=choices,blank=True,default='one')
    survey = models.ForeignKey(Survey,on_delete=models.CASCADE,related_name='questions')
    tone_analyzer = models.CharField(max_length=3,default='No')
    question_number = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.question

class SurveyAnswer(models.Model):

    survey = models.ForeignKey(Survey,on_delete=models.CASCADE,related_name='survey_answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name


class Answer(models.Model):

    surveyanswer = models.ForeignKey(SurveyAnswer,on_delete=models.CASCADE,related_name='answers')
    answer = models.TextField()
    question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name='answers')
    tone_analyzer = models.CharField(max_length=20,default='Not Applicable')

    def __str__(self):
        return self.answer
