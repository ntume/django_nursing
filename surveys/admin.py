from django.contrib import admin
from .models import Survey,Category,Question,Answer,SurveyAnswer

# Register your models here.
admin.site.register(Survey)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(SurveyAnswer)
