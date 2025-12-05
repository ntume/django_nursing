from django import forms
from .models import SIMProcedureLog, Student, StudentEducationPlanSectionWILRequirement, StudentLearningProgramme, StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationAttachment, StudentLearningProgrammeRegistrationRegister, StudentLearningProgrammeVaccination, StudentLogSheet, StudentNextofKin, StudentRegistrationLeave, StudentRegistrationModuleComment, StudentRegistrationModuleEmail,EmailPreferences

class StudentCreateForm(forms.ModelForm):

    class Meta():
        model = Student
        fields = ('first_name','last_name','id_number','email','cellphone','dob',)
        
        
class StudentBasicForm(forms.ModelForm):

    class Meta():
        model = Student
        fields = ('first_name','last_name','id_number','email',)
        

class StudentProfileForm(forms.ModelForm):

    class Meta():
        model = Student
        fields = ('first_name',
                  'last_name',
                  'id_number',
                  'email',
                  'cellphone',
                  'dob',
                  'age',
                  'disability',
                  'type_of_area',
                  'physical_address_1',
                  'physical_address_2',
                  'postal_address_1',
                  'postal_address_2',
                  'marital_status',)

class StudentProfilePicForm(forms.ModelForm):

    class Meta():
        model = Student
        fields = ('profile_pic',)



class StudentNextofKinForm(forms.ModelForm):

    class Meta():
        model = StudentNextofKin
        fields = ('first_name',
                  'type_of_id',
                  'last_name',
                  'id_number',
                  'home_address',
                  'postal_address',
                  'cellphone',
                  'email')



class StudentLearningProgrammeForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgramme
        fields = ('start_date',)



class StudentLearningProgrammeRegistrationForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistration
        fields = ('registration_date',)



class StudentRegistrationModuleCommentForm(forms.ModelForm):

    class Meta():
        model = StudentRegistrationModuleComment
        fields = ('comment',)



class StudentRegistrationModuleEmailForm(forms.ModelForm):

    class Meta():
        model = StudentRegistrationModuleEmail
        fields = ('title','email',)


class EmailPreferencesForm(forms.ModelForm):

    class Meta():
        model = EmailPreferences
        fields = ('adverts','events','workshops','surveys')



class LearnerExtendedForm(forms.ModelForm):

    class Meta():
        model = Student
        fields = ('first_name',
                  'last_name',
                  'id_number',
                  'title',
                  'disability',
                  'dob',
                  'marital_status','age')
        
class LearnerAddressForm(forms.ModelForm):

    class Meta():
        model = Student
        fields = (
            'physical_address_1',
            'postal_address_1',
            'physical_address_2',
            'postal_address_2',
            'physical_address_3',
            'postal_address_3',
            'cellphone',
        )
        
        
class LearnerEducationForm(forms.ModelForm):
    
    class Meta():
        model = Student
        fields = (
            'marticulated',
        )


class LearnerNextKinForm(forms.ModelForm):

    class Meta():
        model = StudentNextofKin
        fields = ('first_name','last_name','home_address','telephone','cellphone','home_number','relationship')


class LearnerAttachementIDForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'id_copy',)
        

class LearnerAttachementSancLearnerRegistrationForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'sanc_learner_registration',)     
        
        

class LearnerAttachementMatricForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'matric_certificate',)
        

class LearnerAttachementMarriageForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'marriage_certificate',)
        

class LearnerAttachementOtherQualificationForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'other_qualification',)
        
class LearnerAttachementIndemnityForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'indemnity',)
        

class LearnerAttachementSancCertificateForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'sanc_certificate',)
        
class LearnerAttachementAuxillaryCertificateForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'auxilary_certificate',)
        
class LearnerAttachementPracticingCertificateForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'practicing_certificate',)
        

class LearnerAttachementSAQAForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'saqa_evaluation',)
        

class LearnerAttachementStudyPermitForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationAttachment
        fields = (
            'study_permit',)
        

class StudentRegistrationLeaveForm(forms.ModelForm):

    class Meta():
        model = StudentRegistrationLeave
        fields = (
            'from_date','to_date','comment',)
        
        
class StudentRegistrationLeaveFileForm(forms.ModelForm):

    class Meta():
        model = StudentRegistrationLeave
        fields = ('file',)
        
        
class StudentEducationPlanSectionWILRequirementForm(forms.ModelForm):

    class Meta():
        model = StudentEducationPlanSectionWILRequirement
        fields = (
            'hours','credits',)  
        
        
class StudentLogSheetForm(forms.ModelForm):

    class Meta():
        model = StudentLogSheet
        fields = ('student_impression','student_comment','date','end_date')     
        

class SIMProcedureLogForm(forms.ModelForm):

    class Meta():
        model = SIMProcedureLog
        fields = ('start','end','date')    


class StudentLearningProgrammeRegistrationRegisterForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeRegistrationRegister
        fields = ('date','start_time','end_time')  
        
        
class StudentLearningProgrammeVaccinationForm(forms.ModelForm):

    class Meta():
        model = StudentLearningProgrammeVaccination
        fields = ('batch_number','expiry_date','administration_site','administration_date',)  
        