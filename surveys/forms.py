from django import forms
from .models import Category, Question, Survey


class SurveyForm(forms.ModelForm):

    class Meta():
        model = Survey
        exclude = ["created_at","published","user"]

class QuestionForm(forms.ModelForm):

    class Meta():
        model = Question
        fields = ('question','type','choice')


class CategoryForm(forms.ModelForm):

    class Meta():
        model = Category
        fields = ('category',)
