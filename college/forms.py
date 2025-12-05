from django import forms
from .models import CohortRegistrationCompulsoryProcedure, CohortRegistrationPeriodEducationPlan, CohortRegistrationPeriodModule, CohortRegistrationPeriodModuleFormative, CohortRegistrationPeriodModuleRegister, CohortRegistrationProcedure, CohortRegistrationProcedureSummative, CohortRegistrationProcedureSummativeTaskAssessment, CohortRegistrationProcedureTaskAssessment, CollegeCampus, EducationPlanYear, EducationPlanYearSection, EducationPlanYearSectionWILRequirement, EducationPlanYearSectionWeeks, ExternalStaff, HealthCareFacility, HealthCareFacilityDisciplineNumber, HealthCareFacilityHOD, HealthCareFacilityLearningProgrammeNumbers, LPRegistrationPeriodModuleFormative, LearningProgramme, LearningProgrammeBlockTemplate, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod, LearningProgrammeCompetency, LearningProgrammeCompetencyBreakdown, LearningProgrammeDocument, LearningProgrammeELO, LearningProgrammeELOAssessmentCriteria, LearningProgrammeModule, LearningProgrammeModuleFormative, LearningProgrammeModuleStudyUnit, LearningProgrammeModuleStudyUnitSection, LearningProgrammePeriod, LearningProgrammePeriodModerationCriteria, LearningProgrammePeriodModerationCriteriaWIL, LearningProgrammePeriodRegistrationModule, LearningProgrammePeriodTimeTableSession, LearningProgrammePeriodWILBlockHours, LearningProgrammePeriodWILRequirement, LearningProgrammeSimulationTheme, LearningProgrammeSimulationThemeActivities, Moderator, RegistrationPeriod, Staff  

class CollegeCampusForm(forms.ModelForm):

    class Meta():
        model = CollegeCampus
        fields = ('name','physical_address_1','physical_address_2')
        
        
class HealthCareFacilityForm(forms.ModelForm):

    class Meta():
        model = HealthCareFacility
        fields = ('name','physical_address_1','physical_address_2','code','category',)



class HealthCareFacilityDisciplineNumberForm(forms.ModelForm):

    class Meta():
        model = HealthCareFacilityDisciplineNumber
        fields = ('student_numbers',)
        
        

class HealthCareFacilityLearningProgrammeNumbersForm(forms.ModelForm):

    class Meta():
        model = HealthCareFacilityLearningProgrammeNumbers
        fields = ('student_numbers',)


class HealthCareFacilityHODForm(forms.ModelForm):

    class Meta():
        model = HealthCareFacilityHOD
        fields = ('first_name','last_name','email','contact','title',)


class StaffForm(forms.ModelForm):

    class Meta():
        model = Staff
        fields = ('first_name','last_name','email','contact','title','staff_number')



class ExternalStaffForm(forms.ModelForm):

    class Meta():
        model = ExternalStaff
        fields = ('first_name','last_name','email',)
        
        
class ModeratorForm(forms.ModelForm):

    class Meta():
        model = Moderator
        fields = ('first_name','last_name','email','contact','title',)


class LearningProgrammeForm(forms.ModelForm):

    class Meta():
        model = LearningProgramme
        fields = ('programme_name','programme_code','total_credits','duration')


class LearningProgrammePeriodForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammePeriod
        fields = ('period','position')


class LearningProgrammeDocumentForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeDocument
        fields = ('title','description',)


class LearningProgrammeDocumentFileForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeDocument
        fields = ('document',)


class LearningProgrammeELOForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeELO
        fields = ('title','description','position')


class LearningProgrammeELOAssessmentCriteriaForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeELOAssessmentCriteria
        fields = ('description',)

class LearningProgrammeCompetencyForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeCompetency
        fields = ('title',)

class LearningProgrammeCompetencyBreakdownForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeCompetencyBreakdown
        fields = ('description',)

class LearningProgrammeModuleForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeModule
        fields = ('module_name',
                  'module_code',
                  'credits',
                  'module_type',
                  'theory_credits',
                  'wil_credits',
                  'theory_hours',
                  'wil_hours',
                  'entrance_year_mark',
                  'summative_weight',
                  'assignment_weight',
                  'test_weight')



class LearningProgrammeModuleFormativeForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeModuleFormative
        fields = ('title',
                  'assessment_type',
                  'weight',)
        
class LearningProgrammeModuleStudyUnitForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeModuleStudyUnit
        fields = ('study_unit_name','study_unit_code','credits',)

class LearningProgrammeModuleStudyUnitSectionForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeModuleStudyUnitSection
        fields = ('section','section_code',)


class LearningProgrammeCohortForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeCohort
        fields = ('title','start_date','end_date')


class LearningProgrammeCohortRegistrationPeriodForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeCohortRegistrationPeriod
        fields = ('title','start_date','end_date')


class LearningProgrammeSimulationThemeForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeSimulationTheme
        fields = ('title','number',)

class LearningProgrammeSimulationThemeActivitiesForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeSimulationThemeActivities
        fields = ('description','number',)
        
        
class EducationPlanYearForm(forms.ModelForm):

    class Meta():
        model = EducationPlanYear
        fields = ('year','academic_week_start',)
        

class EducationPlanYearSectionForm(forms.ModelForm):

    class Meta():
        model = EducationPlanYearSection
        fields = ('section','start_date','end_date',)
        
        
class LearningProgrammeBlockTemplateForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammeBlockTemplate
        fields = ('academic_week',)


class LearningProgrammeCohortRegistrationPeriodEducationPlanForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationPeriodEducationPlan
        fields = ('academic_week',)
        
        
class EducationPlanYearSectionWeeksForm(forms.ModelForm):

    class Meta():
        model = EducationPlanYearSectionWeeks
        fields = ('academic_week_number',)
        
        
class LearningProgrammePeriodWILRequirementForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammePeriodWILRequirement
        fields = ('hours','credits',)


class LearningProgrammePeriodWILBlockHoursForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammePeriodWILBlockHours
        fields = ('hours','credits',)
            
        
class EducationPlanYearSectionWILRequirementForm(forms.ModelForm):

    class Meta():
        model = EducationPlanYearSectionWILRequirement
        fields = ('hours','credits',)        
        
        
class CohortRegistrationCompulsoryProcedureForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationCompulsoryProcedure
        fields = ('weights',) 
        
        
class CohortRegistrationProcedureForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationProcedure
        fields = ('weights','compulsory',) 


class CohortRegistrationProcedureSummativeForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationProcedureSummative
        fields = ('weights',) 
        
        
class CohortRegistrationProcedureTaskAssessmentForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationProcedureTaskAssessment
        fields = ('question','question_type','number','penalty') 
        

class CohortRegistrationProcedureSummativeTaskAssessmentForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationProcedureSummativeTaskAssessment
        fields = ('question','question_type','number','penalty') 


class CohortRegistrationPeriodModuleForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationPeriodModule
        fields = ('entrance_year_mark','summative_weight','assignment_weight','test_weight')         
        
        
class CohortRegistrationPeriodModuleFormativeForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationPeriodModuleFormative
        fields = ('assessment_type','title','weight',)  
        
        
class RegistrationPeriodForm(forms.ModelForm):

    class Meta():
        model = RegistrationPeriod
        fields = ('name','start_date','end_date','active')  
        
        
class LearningProgrammePeriodRegistrationModuleForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammePeriodRegistrationModule
        fields = ('entrance_year_mark','summative_weight','assignment_weight','test_weight')         
        
class LPRegistrationPeriodModuleFormativeForm(forms.ModelForm):

    class Meta():
        model = LPRegistrationPeriodModuleFormative
        fields = ('assessment_type','title','weight') 



class LearningProgrammePeriodTimeTableSessionForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammePeriodTimeTableSession
        fields = ('title','start_time','end_time') 
        
        
class LearningProgrammePeriodModerationCriteriaForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammePeriodModerationCriteria
        fields = ('criteria','question_type','number') 
        


class LearningProgrammePeriodModerationCriteriaWILForm(forms.ModelForm):

    class Meta():
        model = LearningProgrammePeriodModerationCriteriaWIL
        fields = ('criteria','question_type','number') 


class CohortRegistrationPeriodModuleRegisterForm(forms.ModelForm):

    class Meta():
        model = CohortRegistrationPeriodModuleRegister
        fields = ('date','time',)