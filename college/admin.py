from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(LearningProgrammeCompetency)
admin.site.register(LearningProgrammeCompetencyBreakdown)
admin.site.register(LearningProgrammeModule)
admin.site.register(LearningProgrammeModuleStudyUnit)
admin.site.register(LearningProgrammeModuleStudyUnitSection)
admin.site.register(LearningProgrammeCohort)
admin.site.register(LearningProgrammeELOAssessmentCriteria)
admin.site.register(LearningProgrammeELO)
admin.site.register(LearningProgrammeDocument)
admin.site.register(LearningProgrammePeriod)
admin.site.register(LearningProgramme)
admin.site.register(Staff)
admin.site.register(CollegeCampus)

