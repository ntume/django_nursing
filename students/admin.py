from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Student)
admin.site.register(StudentNextofKin)
admin.site.register(StudentLearningProgramme)
admin.site.register(StudentLearningProgrammeRegistration)
admin.site.register(StudentRegistrationModule)
admin.site.register(StudentRegistrationModuleComment)
admin.site.register(StudentRegistrationModuleEmail)
admin.site.register(EmailPreferences)
