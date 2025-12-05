from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Category,Survey,Question,SurveyAnswer,Answer
from evaluations.models import QuestionType,QuestionTypeOptions

class SurveyModelSerializer(serializers.ModelSerializer):
    """Serizliser class for Surveys """

    class Meta:
        model = Survey
        fields = ('id','title','description','category','created_at',)
        read_only_fields = ('id',)
        depth = 1


class SurveyCategoriesModelSerializer(serializers.ModelSerializer):
    """Serizliser class for Category """

    class Meta:
        model = Category
        fields = ('id','category',)
        read_only_fields = ('id',)


class SurveyQuestionsModelSerializer(serializers.ModelSerializer):
    """Serizliser class for Questions """

    class Meta:
        model = Question
        fields = ('id','question','type')
        read_only_fields = ('id',)
        depth = 2


class SurveyAnswersModelSerializer(serializers.ModelSerializer):
    """Serizliser class for Survey Anser """

    class Meta:
        model = SurveyAnswer
        fields = ('id','survey','user','created_at')
        read_only_fields = ('id',)


class AnswersModelSerializer(serializers.ModelSerializer):
    """Serizliser class for Ansers """

    class Meta:
        model = Answer
        fields = ('id','surveyanswer','answer','question')
        read_only_fields = ('id',)


class SurveyModelRelationshipSerializer(serializers.ModelSerializer):
    """Serizliser class for Surveys """

    survey_questions = SurveyQuestionsModelSerializer(many = False,read_only=True)

    class Meta:
        model = Survey
        fields = ('id','title','description','category','created_at','survey_questions',)
        read_only_fields = ('id',)
        depth = 1


class QuestionTypeOptionsModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionTypeOptions
        fields = ('id','type','option','value')
        read_only_fields = ('id',)


class QuestionTypeModelRelationshipSerializer(serializers.ModelSerializer):

    type_options = QuestionTypeOptionsModelSerializer(many = False,read_only=True)

    class Meta:
        model = QuestionType
        fields = ('id','type','options','type_options')
        read_only_fields = ('id',)
