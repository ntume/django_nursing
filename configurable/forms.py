from django import forms
from .models import *


class CountryForm(forms.ModelForm):

    class Meta():
        model = Country
        fields = ('country','country_code',)

class CityForm(forms.ModelForm):

    class Meta():
        model = City
        fields = ('city',)

class SuburbForm(forms.ModelForm):

    class Meta():
        model = Suburb
        fields = ('suburb','postal_code',)


class ProvinceForm(forms.ModelForm):

    class Meta():
        model = Province
        fields = ('province',)

class MunicipalityForm(forms.ModelForm):

    class Meta():
        model = Municipality
        fields = ('municipality',)


class DistrictForm(forms.ModelForm):

    class Meta():
        model = District
        fields = ('district',)


class LanguageForm(forms.ModelForm):

    class Meta():
        model = Language
        fields = ('language',)

class NQFLevelForm(forms.ModelForm):

    class Meta():
        model = NQFLevel
        fields = ('nqf_level','description','code',)

class GenderForm(forms.ModelForm):

    class Meta():
        model = Gender
        fields = ('gender',)


class DisabilityForm(forms.ModelForm):

    class Meta():
        model = Disability
        fields = ('disability',)      


class RaceForm(forms.ModelForm):

    class Meta():
        model = Race
        fields = ('race',)  


class EconomicStatusForm(forms.ModelForm):

    class Meta():
        model = EconomicStatus
        fields = ('status',)  


class EmploymentEconomicStatusForm(forms.ModelForm):

    class Meta():
        model = EmploymentEconomicStatus
        fields = ('status',) 
        
        
class ResidentialStatusForm(forms.ModelForm):
    
    class Meta():
        model = ResidentialStatus
        fields = ('status',) 


class IndustryForm(forms.ModelForm):
    
    class Meta():
        model = Industry
        fields = ('industry','code',) 
    

class QuestionTypeForm(forms.ModelForm):

    class Meta():
        model = QuestionType
        fields = ('type','options')

class QuestionTypeOptionsForm(forms.ModelForm):

    class Meta():
        model = QuestionTypeOptions
        fields = ('value','option')


class TypeOfIDForm(forms.ModelForm):

    class Meta():
        model = TypeOfID
        fields = ('type_of_id','code',)


class StructureStatusIDForm(forms.ModelForm):

    class Meta():
        model = StructureStatusID
        fields = ('status','code',)



class NationalityForm(forms.ModelForm):
    
    class Meta():
        model = Nationality
        fields = ('nationality','code') 

class TypeOfLeaveForm(forms.ModelForm):

    class Meta():
        model = TypeOfLeave
        fields = ('type_of_leave','number_of_days','description',)


class IndemnityForm(forms.ModelForm):

    class Meta():
        model = Indemnity
        fields = ('indemnity',)


class SponsorshipForm(forms.ModelForm):

    class Meta():
        model = Sponsorship
        fields = ('sponsorship',)
        
        
class ProgarmmeBlockForm(forms.ModelForm):

    class Meta():
        model = ProgarmmeBlock
        fields = ('block_code','block_name','wil','internal')



class DemonstrationForm(forms.ModelForm):

    class Meta():
        model = Demonstration
        fields = ('demonstration','duration',)


class DisciplineForm(forms.ModelForm):

    class Meta():
        model = Discipline
        fields = ('discipline',)


class WardForm(forms.ModelForm):

    class Meta():
        model = Ward
        fields = ('ward',)
        

class ClinicalProcedureThemeForm(forms.ModelForm):

    class Meta():
        model = ClinicalProcedureTheme
        fields = ('theme',)
        
        
class ClinicalProcedureThemeTaskForm(forms.ModelForm):

    class Meta():
        model = ClinicalProcedureThemeTask
        fields = ('task','duration',)
        
        
class ClinicalProcedureThemeTaskAssessmentForm(forms.ModelForm):

    class Meta():
        model = ClinicalProcedureThemeTaskAssessment
        fields = ('question','question_type','number','penalty')
        

    def clean_number(self):
        number = self.cleaned_data['number']
        if not all(part.isdigit() for part in number.split('.')):
            raise forms.ValidationError("The number must contain only digits separated by dots.")
        return number
        
        
class ShiftForm(forms.ModelForm):

    class Meta():
        model = ShiftType
        fields = ('shift','shift_code','shift_start','shift_end',)
        
        
class WILScaleQuestionForm(forms.ModelForm):

    class Meta():
        model = WILScaleQuestion
        fields = ('question','simulated',)
        
        
class RegistrationBlockCodeForm(forms.ModelForm):

    class Meta():
        model = RegistrationBlockCode
        fields = ('code','description',)


class RegisterCategoryForm(forms.ModelForm):

    class Meta():
        model = RegisterCategory
        fields = ('category','description',)


class VaccinationDoseForm(forms.ModelForm):

    class Meta():
        model = VaccinationDose
        fields = ('dose',)
        
        
