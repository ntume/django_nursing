import datetime
from django.db import models
from django.dispatch import receiver
from accounts.models import Role, User
from django.core.validators import FileExtensionValidator
from django_nursing.validators import validate_file_size
import uuid
import os
from django.db.models import Sum

from configurable.models import ClinicalProcedureTheme, ClinicalProcedureThemeTask, Discipline, Gender, NQFLevel, ProgarmmeBlock, Race, RegisterCategory, RegistrationBlockCode, Suburb, Ward

def update_file_path(instance, filename):
    """generate file path"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('generaldocuments/',filename)



def update_filename(instance, filename):
    path = "profile/"
    ext = filename.split('.')[-1]
    format = "{}.{}".format(instance.id,ext)
    return os.path.join(path, format)


def update_timetable_path(instance, filename):
    """generate file path"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('college/timetable/',filename)


def staff_profile_signature_file_path(instance, filename):
    """generate file path new file"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('staff/',filename)


# Create your models here.


class RegistrationPeriod(models.Model):
    '''
    Registration Periods
    '''
    
    
    
    name = models.CharField(max_length=100)
    block = models.ForeignKey(RegistrationBlockCode,on_delete=models.SET_NULL,null=True,related_name='registration_periods')
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    active = models.CharField(max_length=3,default='No')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    

class CollegeCampus(models.Model):
    '''
    different branches of the college
    '''

    
    name = models.CharField(max_length=100)
    physical_address_1 = models.CharField(max_length=100)
    physical_address_2 = models.CharField(max_length=100)
    physical_address_3 = models.CharField(max_length=100,null=True)
    postal_code = models.ForeignKey(Suburb,on_delete=models.SET_NULL,null=True,related_name='college_branches')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


class HealthCareFacility(models.Model):
    '''
    different bhealth care facilities
    '''
    
    CATEGORY = (('Primary Health Care','Primary Health Care'),('Hospital','Hospital'))

    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5,blank=True)
    physical_address_1 = models.CharField(max_length=100)
    physical_address_2 = models.CharField(max_length=100)
    physical_address_3 = models.CharField(max_length=100,null=True)
    category = models.CharField(max_length=22,choices=CATEGORY,null=True)
    postal_code = models.ForeignKey(Suburb,on_delete=models.SET_NULL,null=True,related_name='health_care_facilities')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

    def check_numbers_balance(self,lp,registration):
        '''
        Function to check how many more learners can be added to a specific facility in that programme
        '''
        
        today = datetime.date.today()
        
        facility = HealthCareFacility.objects.get(id = self.id)
        check_total_numbers = HealthCareFacilityLearningProgrammeNumbers.objects.filter(health_care_facility = facility,
                                                                                  learning_programme = lp)
        student_numbers = 0
        if check_total_numbers.exists():
            total_numbers = check_total_numbers.first()
            student_numbers = total_numbers.student_numbers
            
        #check how many spots have been occupied and how many left
        
        assigned_registrations = list(facility.students.
                                      filter(registration__student_learning_programme__learning_programme = lp,
                                                   registration__registration_period__start_date__lte = today,
                                                   registration__registration_period__end_date__gte = today).
                                      exclude(registration=registration).
                                      values_list('registration',flat=True))
        
        
        number_assigned = len(set(assigned_registrations))
        return student_numbers - number_assigned



class HealthCareFacilityWard(models.Model):
    '''
    different health care facility wards at a specific facility
    '''
    
    
    ward = models.ForeignKey(Ward,on_delete=models.SET_NULL,null=True,related_name='healthcare_facilities')
    facility = models.ForeignKey(HealthCareFacility,on_delete=models.SET_NULL,null=True,related_name='wards')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
  
  
class HealthCareFacilityHOD(models.Model):
    '''
    different health care facility ward hods
    '''
    
    CATEGORY = (('Primary Health Care','Primary Health Care'),('Hospital','Hospital'))

    
    wards = models.ManyToManyField(HealthCareFacilityWard,related_name='hods')
    facility = models.ForeignKey(HealthCareFacility,on_delete=models.SET_NULL,null=True,related_name='hods')
    title = models.CharField(max_length=10,null=True)
    first_name = models.CharField(max_length=15,null=True)
    last_name = models.CharField(max_length=15,null=True)
    email = models.CharField(max_length=50,null=True)
    contact = models.CharField(max_length=15,null=True)
    gender = models.ForeignKey(Gender,on_delete=models.SET_NULL,null=True,related_name='facility_hod')
    race = models.ForeignKey(Race,on_delete=models.SET_NULL,null=True,related_name='facility_hod')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='facility_hod')
    active = models.CharField(max_length=3,default='Yes')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
    
class Moderator(models.Model):
    '''
    Moderators
    '''

    class Meta:
        ordering = ['last_name'] 

    
    title = models.CharField(max_length=10)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    contact = models.CharField(max_length=15)
    gender = models.ForeignKey(Gender,on_delete=models.SET_NULL,null=True,related_name='moderator')
    race = models.ForeignKey(Race,on_delete=models.SET_NULL,null=True,related_name='moderator')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='moderator')
    active = models.CharField(max_length=3,default='Yes')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
    

class Staff(models.Model):
    '''
    Internal staff users
    '''

    class Meta:
        ordering = ['last_name'] 

    
    title = models.CharField(max_length=10)
    staff_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    contact = models.CharField(max_length=15)
    gender = models.ForeignKey(Gender,on_delete=models.SET_NULL,null=True,related_name='staff')
    race = models.ForeignKey(Race,on_delete=models.SET_NULL,null=True,related_name='staff')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='staff')
    college_campus = models.ForeignKey(CollegeCampus,on_delete=models.SET_NULL,null=True,related_name='staff')
    active = models.CharField(max_length=3,default='Yes')
    signature = models.FileField(upload_to=staff_profile_signature_file_path,null=True,validators=[FileExtensionValidator( ['jpeg','jpg','png'] ),validate_file_size ])
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
class ExternalStaff(models.Model):
    '''
    external  staff co assessors users
    '''

    class Meta:
        ordering = ['last_name'] 

    
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='external_staff')
    facility = models.ForeignKey(HealthCareFacility,on_delete=models.SET_NULL,null=True,related_name='external_staff')
    active = models.CharField(max_length=3,default='Yes')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
class LearningProgramme(models.Model):
    '''
    Class for learning programmes
    '''

    
    programme_name = models.CharField(max_length=100)
    programme_code = models.CharField(max_length=10)
    total_credits = models.PositiveIntegerField()
    duration = models.PositiveIntegerField()
    active = models.CharField(max_length=3,default='Yes')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)



class HealthCareFacilityLearningProgrammeNumbers(models.Model):

    ''''
    The number of students that can be taken by each facility
    '''

    health_care_facility = models.ForeignKey(HealthCareFacility,on_delete=models.CASCADE,related_name='learning_programme_numbers')
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.CASCADE,related_name='health_care_facility_numbers')
    student_numbers = models.PositiveIntegerField()
    
    
class HealthCareFacilityDisciplineNumber(models.Model):

    ''''
    The number of students that can be taken by each facility
    '''

    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.CASCADE,null=True,related_name='discipline_numbers')
    health_care_facility = models.ForeignKey(HealthCareFacility,on_delete=models.CASCADE,related_name='discipline_numbers')
    discipline = models.ForeignKey(Discipline,on_delete=models.CASCADE,related_name='discipline_numbers')
    student_numbers = models.PositiveIntegerField()


class LearningProgrammePeriod(models.Model):
    '''
    learning programme years
    '''

    class Meta:
        ordering = ['position']

    period = models.CharField(max_length=20)
    position = models.PositiveIntegerField()
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='periods')
    created_at = models.DateTimeField(auto_now_add=True)


class LearningProgrammePeriodTimeTableSession(models.Model):
    '''
    Timetable sessions per day
    '''
    
    class Meta:
        ordering = ['title']

    
    title = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='timetable_sessions')
    learning_programme_period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.CASCADE,related_name='timetable_sessions')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


class LearningProgrammePeriodModerationCriteria(models.Model):
    '''
    procedure assessments
    '''
    
    CHOICES = (('Note','Note'),('Heading','Heading'),('Question','Question'))
    
    CHOICES_ROLE = (('Lecturer','Lecturer'),('Moderator','Moderator'))

    class Meta:
        ordering = ['number']

    learning_programme_period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.CASCADE,related_name='moderation_criteria')
    criteria = models.TextField()
    question_type = models.CharField(max_length=10,choices=CHOICES,default='Question')
    number = models.CharField(max_length=20)
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='moderation_criteria')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure each level of the number is zero-padded
        self.number = '.'.join(f"{int(part):02}" for part in self.number.split('.'))
        super().save(*args, **kwargs)
        
    @property
    def original_number(self):
        # Remove padding for display
        return '.'.join(str(int(part)) for part in self.number.split('.'))

    def __str__(self):
        # Use the unpadded number for display purposes
        return f"{self.original_number} - {self.question}"
    
    
    
class LearningProgrammePeriodModerationCriteriaWIL(models.Model):
    '''
    procedure assessments
    '''
    
    CHOICES = (('Note','Note'),('Heading','Heading'),('Question','Question'))
    
    CHOICES_ROLE = (('Lecturer','Lecturer'),('Moderator','Moderator'))

    class Meta:
        ordering = ['number']

    learning_programme_period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.CASCADE,related_name='moderation_criteria_wil')
    criteria = models.TextField()
    question_type = models.CharField(max_length=10,choices=CHOICES,default='Question')
    number = models.CharField(max_length=20)
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='moderation_criteria_wil')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure each level of the number is zero-padded
        self.number = '.'.join(f"{int(part):02}" for part in self.number.split('.'))
        super().save(*args, **kwargs)
        
    @property
    def original_number(self):
        # Remove padding for display
        return '.'.join(str(int(part)) for part in self.number.split('.'))

    def __str__(self):
        # Use the unpadded number for display purposes
        return f"{self.original_number} - {self.question}"


    
class LearningProgrammePeriodRegistration(models.Model):
    '''
    learning programme period registrations
    '''


    learning_programme_period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.CASCADE,related_name='registrations')
    registration_period = models.ForeignKey(RegistrationPeriod,on_delete=models.CASCADE,related_name='programmes')
    created_at = models.DateTimeField(auto_now_add=True)
    





class LearningProgrammePeriodWILRequirement(models.Model):
    '''
    Wil requirements per period
    '''

    period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.CASCADE,related_name='wil_requirements')
    discipline = models.ForeignKey(Discipline,null=True,related_name='wil_requirements',on_delete=models.CASCADE)
    hours = models.DecimalField(decimal_places=1,max_digits=4,default=0.0)
    credits = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def check_hour_balance_sections(self):
        '''
        Function to check how many hours have been allocated to teh sections
        '''        
        wil_requirement = LearningProgrammePeriodWILRequirement.objects.get(id = self.id)
        
        allocated_hours = wil_requirement.section_wil_requirements.all().aggregate(Sum('hours'))['hours__sum'] or 0 

        balance = wil_requirement.hours - allocated_hours
        
        return balance
    


class LearningProgrammePeriodWILBlockHours(models.Model):
    '''
    Block requirements per period
    '''

    period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.CASCADE,related_name='block_hours')
    block = models.ForeignKey(ProgarmmeBlock,null=True,related_name='block_hours',on_delete=models.CASCADE)
    hours = models.DecimalField(decimal_places=1,max_digits=4,default=0.0)
    credits = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class LearningProgrammeDocument(models.Model):

    """
    General documents for Learning Programme
    """

    document = models.FileField(blank=True,upload_to=update_file_path)
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='documents')
    title = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.CharField(max_length=3,default='Yes')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='learning_programme_documents',null=True)

    def __str__(self):
        return self.title


class LearningProgrammeELO(models.Model):
    '''
    class for exit level outcomes
    '''

    title = models.CharField(max_length = 50)
    description = models.TextField()
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='elos')
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField()


class LearningProgrammeELOAssessmentCriteria(models.Model):
    '''
    Assessment Criteria
    '''

    description = models.TextField()
    elo = models.ForeignKey(LearningProgrammeELO,on_delete=models.SET_NULL,null=True,related_name='assessment_criteria')
    created_at = models.DateTimeField(auto_now_add=True)


class LearningProgrammeCompetency(models.Model):
    '''
    Competency table
    '''

    title = models.CharField(max_length=250)
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='competencies')
    created_at = models.DateTimeField(auto_now_add=True)


class LearningProgrammeCompetencyBreakdown(models.Model):
    '''
    competency breakdown
    '''

    description = models.CharField(max_length=256)
    competency = models.ForeignKey(LearningProgrammeCompetency,on_delete=models.SET_NULL,null=True,related_name='breakdown')
    created_at = models.DateTimeField(auto_now_add=True)

class LearningProgrammeModule(models.Model):
    '''
    Modules for a learning programme
    '''
    
    CHOICES_TYPE = (('Core','Core'),('Fundamental','Fundamental'))

    
    module_name = models.CharField(max_length=100)
    module_code = models.CharField(max_length=10)
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='modules')
    credits = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    nqf_level = models.ForeignKey(NQFLevel,on_delete=models.SET_NULL,null=True,related_name='modules')
    module_type = models.CharField(max_length=15,null=True,choices=CHOICES_TYPE)
    theory_credits = models.PositiveIntegerField(default=0)
    wil_credits = models.PositiveIntegerField(default=0)
    theory_hours = models.PositiveIntegerField(default=0)
    wil_hours = models.PositiveIntegerField(default=0)
    entrance_year_mark = models.PositiveIntegerField(default=0)
    summative_weight = models.PositiveIntegerField(default=0)
    assignment_weight = models.PositiveIntegerField(default=0)
    test_weight = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    


class LearningProgrammePeriodRegistrationModule(models.Model):
    '''
    registartion modules
    '''

    learning_programme_period_registration_period = models.ForeignKey(LearningProgrammePeriodRegistration,on_delete=models.SET_NULL,null=True,related_name='modules')
    module = models.ForeignKey(LearningProgrammeModule,on_delete=models.SET_NULL,null=True,related_name='registeration_modules')
    entrance_year_mark = models.PositiveIntegerField()
    summative_weight = models.PositiveIntegerField()
    assignment_weight = models.PositiveIntegerField(default=0)
    test_weight = models.PositiveIntegerField(default=0)
    
class LPRegistrationPeriodModuleFormative(models.Model):
    '''
    formative tests for that registration period
    ''' 
    CHOICES = (('Assignment','Assignment'),('Test','Test'))
    
    module = models.ForeignKey(LearningProgrammePeriodRegistrationModule,on_delete=models.CASCADE,null=True,related_name='formative')
    assessment_type = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    weight = models.PositiveIntegerField()
    
class LearningProgrammePeriodModule(models.Model):
    '''
    learning programme period modules
    '''

    period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.CASCADE,related_name='modules')
    module = models.ForeignKey(LearningProgrammeModule,on_delete=models.SET_NULL,null=True,related_name='period')
    created_at = models.DateTimeField(auto_now_add=True)
    
class LearningProgrammeModulePrerequisite(models.Model):
    
    
    module = models.ForeignKey(LearningProgrammeModule,on_delete=models.SET_NULL,null=True,related_name='prerequisites')
    prerequisite = models.ForeignKey(LearningProgrammeModule,on_delete=models.SET_NULL,null=True,related_name='postrequisites')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


class LearningProgrammeModuleFormative(models.Model):
    '''
    formative tests boilerplate
    ''' 
    CHOICES = (('Assignment','Assignment'),('Test','Test'))
    
    module = models.ForeignKey(LearningProgrammeModule,on_delete=models.CASCADE,null=True,related_name='formative')
    assessment_type = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    weight = models.PositiveIntegerField()


class LearningProgrammeModuleStudyUnit(models.Model):
    '''
    Module Study units
    '''

    
    study_unit_name = models.CharField(max_length=100)
    study_unit_code = models.CharField(max_length=10)
    module = models.ForeignKey(LearningProgrammeModule,on_delete=models.SET_NULL,null=True,related_name='study_units')
    credits = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


class LearningProgrammeModuleStudyUnitSection(models.Model):
    '''
    Study unit sections
    '''

    
    section = models.CharField(max_length=100)
    section_code = models.CharField(max_length=10)
    study_unit = models.ForeignKey(LearningProgrammeModuleStudyUnit,on_delete=models.SET_NULL,null=True,related_name='study_unit_sections')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)



  
class LearningProgrammeSimulationTheme(models.Model):
    '''
    Competency table
    '''

    title = models.CharField(max_length=250)
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='themes')
    number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class LearningProgrammeSimulationThemeActivities(models.Model):
    '''
    competency breakdown
    '''

    description = models.TextField()
    theme = models.ForeignKey(LearningProgrammeSimulationTheme,on_delete=models.SET_NULL,null=True,related_name='activities')
    number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class LearningProgrammeCohort(models.Model):
    '''
    Yearly cohort of the learning programme cohort
    '''

    
    title = models.CharField(max_length=50)
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='cohorts')
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    student_cards = models.FileField(upload_to=update_filename, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)



class LearningProgrammeCohortRegistrationPeriod(models.Model):
    '''
    Yearly cohort of the learning programme cohort
    '''

    
    title = models.CharField(max_length=50)
    learning_programme_cohort = models.ForeignKey(LearningProgrammeCohort,on_delete=models.SET_NULL,null=True,related_name='registration_periods')
    period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.SET_NULL,null=True,related_name='registration_periods')
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    programme_coordinator = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='programmes')
    summative_procedures_moderators = models.ManyToManyField(Moderator,related_name='programmes')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

class CohortRegistrationPeriodModule(models.Model):
    '''
    registartion modules
    '''

    cohort_registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='modules')
    module = models.ForeignKey(LearningProgrammeModule,on_delete=models.SET_NULL,null=True,related_name='modules')
    entrance_year_mark = models.PositiveIntegerField()
    summative_weight = models.PositiveIntegerField()
    assignment_weight = models.PositiveIntegerField(default=0)
    test_weight = models.PositiveIntegerField(default=0)
    lecturer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='module_lecturers')
    moderator = models.ForeignKey(Moderator,on_delete=models.SET_NULL,null=True,related_name='modules')



class CohortRegistrationPeriodModuleRegister(models.Model):
    '''
    Moderation Report
    '''
    
     
    module = models.ForeignKey(CohortRegistrationPeriodModule,on_delete=models.SET_NULL,null=True,related_name='registers')
    date = models.DateField(blank = True)
    time = models.TimeField(blank = True)
    unit = models.ForeignKey(LearningProgrammeModuleStudyUnit,on_delete=models.SET_NULL,null=True,related_name='registers')
    created_at = models.DateTimeField(auto_now_add=True) 
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='model_registers')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)



class CohortRegistrationPeriodModuleRegisterStudents(models.Model):
    '''
    Register Students
    '''
    
     
    register = models.ForeignKey(CohortRegistrationPeriodModuleRegister,on_delete=models.SET_NULL,null=True,related_name='students')   
    student = models.ForeignKey('students.StudentLearningProgrammeRegistration',on_delete=models.SET_NULL,null=True,related_name='student_registers')
    created_at = models.DateTimeField(auto_now_add=True) 
    status = models.CharField(max_length=10,default='Pending')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


    
class CohortRegistrationPeriodModuleModerationReport(models.Model):
    '''
    Moderation Report
    '''
    
     
    module = models.ForeignKey(CohortRegistrationPeriodModule,on_delete=models.SET_NULL,null=True,related_name='moderation_report')
    comment = models.TextField(blank = True)
    moderators_feedback = models.TextField(blank = True)
    recommendations = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True) 
    moderator = models.ForeignKey(Moderator,on_delete=models.SET_NULL,null=True,related_name='moderation_report')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
class CohortRegistrationPeriodModuleModerationReportAnswers(models.Model):
    '''
    Moderation Criteria
    '''
    
    CHOICES = (('Yes','Yes'),('No','No'),('Not Applicable','Not Applicable'))
    
     
    report = models.ForeignKey(CohortRegistrationPeriodModuleModerationReport,on_delete=models.SET_NULL,null=True,related_name='moderation_criteria')
    assessment = models.ForeignKey(LearningProgrammePeriodModerationCriteria,on_delete=models.CASCADE,related_name='moderation_criteria')
    answer = models.CharField(max_length=20,choices=CHOICES,blank=True)
    remarks = models.TextField(blank = True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='moderation_criteria')
    created_at = models.DateTimeField(auto_now_add=True) 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
    


class CohortRegistrationPeriodModuleFormative(models.Model):
    '''
    formative tests for that registration period
    ''' 
    CHOICES = (('Assignment','Assignment'),('Test','Test'))
    
    module = models.ForeignKey(CohortRegistrationPeriodModule,on_delete=models.CASCADE,null=True,related_name='formative')
    assessment_type = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    weight = models.PositiveIntegerField()
    

class CohortRegistrationCompulsoryProcedure(models.Model):
    '''
    learning programme education paln
    '''


    procedure = models.ForeignKey(ClinicalProcedureThemeTask,on_delete=models.SET_NULL,null=True,related_name='compulsory_procedures')
    cohort_registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='compulsory_procedures')
    weights = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class CohortRegistrationProcedure(models.Model):
    '''
    period procedures
    '''

    class Meta:
        ordering = ['-weights']


    procedure = models.ForeignKey(ClinicalProcedureThemeTask,on_delete=models.SET_NULL,null=True,related_name='cohort_period_procedures')
    cohort_registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='cohort_period_procedures')
    compulsory = models.CharField(max_length=3,default='No')
    weights = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    lecturer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='procedure_lecturer')
    clinical_facilitator = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='procedure_clinical_facilitator')
    lecturer_demonstration = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='procedure_lecturer_demonstration')
    clinical_facilitator_demonstration = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='procedure_clinical_facilitator_demonstration')
    co_assessor = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='procedure_co_assessor')
    

class CohortRegistrationProcedureSummative(models.Model):

    #procedures for summative assessments

    procedure = models.ForeignKey(ClinicalProcedureThemeTask,on_delete=models.SET_NULL,null=True,related_name='cohort_period_summative_procedures')
    cohort_registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='cohort_period_summative_procedures')
    weights = models.PositiveIntegerField(default=0)
    assessor = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='summative_procedure_lecturer')
    clinical_facilitator = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='summative_procedure_clinical_facilitator')
    co_assessor = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='summative_procedure_co_assessor')
    
    
class CohortRegistrationProcedureTaskAssessment(models.Model):
    '''
    procedure assessments
    '''
    
    CHOICES = (('Note','Note'),('Heading','Heading'),('Question','Question'))

    class Meta:
        ordering = ['number']

    task = models.ForeignKey(CohortRegistrationProcedure,on_delete=models.CASCADE,related_name='assessments')
    question = models.TextField()
    question_type = models.CharField(max_length=10,choices=CHOICES,default='Question')
    number = models.CharField(max_length=20)
    penalty = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure each level of the number is zero-padded
        self.number = '.'.join(f"{int(part):02}" for part in self.number.split('.'))
        super().save(*args, **kwargs)
        
    @property
    def original_number(self):
        # Remove padding for display
        return '.'.join(str(int(part)) for part in self.number.split('.'))

    def __str__(self):
        # Use the unpadded number for display purposes
        return f"{self.original_number} - {self.question}"



class CohortRegistrationProcedureSummativeTaskAssessment(models.Model):
    '''
    summative procedure assessments
    '''
    
    CHOICES = (('Note','Note'),('Heading','Heading'),('Question','Question'))

    class Meta:
        ordering = ['number']

    task = models.ForeignKey(CohortRegistrationProcedureSummative,on_delete=models.CASCADE,related_name='assessments')
    question = models.TextField()
    question_type = models.CharField(max_length=10,choices=CHOICES,default='Question')
    number = models.CharField(max_length=20)
    penalty = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure each level of the number is zero-padded
        self.number = '.'.join(f"{int(part):02}" for part in self.number.split('.'))
        super().save(*args, **kwargs)
        
    @property
    def original_number(self):
        # Remove padding for display
        return '.'.join(str(int(part)) for part in self.number.split('.'))

    def __str__(self):
        # Use the unpadded number for display purposes
        return f"{self.original_number} - {self.question}"
    
    
class LearningProgrammeBlockTemplate(models.Model):
    '''
    learning programme years
    '''

    class Meta:
        ordering = ['academic_week']
        
    facility_choices = (('PHC','PHC'),('H','H'),('C','C'))
    time_choices = (('Night','Night'),('Day','Day'))

    block = models.ForeignKey(ProgarmmeBlock,on_delete=models.SET_NULL,null=True,related_name='learning_programme_block_template')
    academic_week = models.PositiveIntegerField()
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.SET_NULL,null=True,related_name='block_template')
    period = models.ForeignKey(LearningProgrammePeriod,on_delete=models.SET_NULL,null=True,related_name='block_template')
    created_at = models.DateTimeField(auto_now_add=True)
    facility_type = models.CharField(max_length=3,null=True)
    time_period = models.CharField(max_length=5,choices=time_choices)



class CohortRegistrationPeriodEducationPlan(models.Model):
    '''
    learning programme education paln
    '''

    class Meta:
        ordering = ['academic_week']
        
    facility_choices = (('PHC','PHC'),('H','H'),('C','C'))
    time_choices = (('Night','Night'),('Day','Day'))

    block = models.ForeignKey(ProgarmmeBlock,on_delete=models.SET_NULL,null=True,related_name='cohort_period')
    academic_week = models.PositiveIntegerField()
    cohort_registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='master_education_plan')
    created_at = models.DateTimeField(auto_now_add=True)
    facility_type = models.CharField(max_length=3,null=True)
    time_period = models.CharField(max_length=5,choices=time_choices,null=True)


    
    
class EducationPlanYear(models.Model):
    '''
    Year for the education plan
    '''
    
    year = models.PositiveIntegerField()
    academic_week_start = models.PositiveSmallIntegerField()
    finalized = models.CharField(max_length=3,default='No')
    cohort_registration_period = models.OneToOneField(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='education_plan')   
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(blank=True,upload_to=update_file_path,null=True)


class EducationPlanYearSection(models.Model):
    '''
    The weeks in that year
    '''
    
    CHOICES = (('1ST QUARTER','1ST QUARTER'),
              ('2ND QUARTER','2ND QUARTER'),
              ('3RD QUARTER','3RD QUARTER'),
              ('4TH QUARTER','4TH QUARTER'),)
    
    education_plan_year = models.ForeignKey(EducationPlanYear,on_delete=models.CASCADE,related_name='sections')
    section = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True) 
    
    
class EducationPlanYearSectionWILRequirement(models.Model):  
    '''
    Quarter Wil Requirements
    '''
    
    education_plan_year_section = models.ForeignKey(EducationPlanYearSection,on_delete=models.CASCADE,related_name='wil_requirements',null=True)
    period_wil_requirement = models.ForeignKey(LearningProgrammePeriodWILRequirement,on_delete=models.CASCADE,related_name='section_wil_requirements')
    hours = models.DecimalField(decimal_places=1,max_digits=4,default=0.0)
    credits = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
     
    
    

class EducationPlanYearSectionWeeks(models.Model):
    '''
    The weeks in that year
    '''

    facility_choices = (('PHC','PHC'),('H','H'),('C','C'))
    time_choices = (('Night','Night'),('Day','Day'))
    
    education_plan_year_section = models.ForeignKey(EducationPlanYearSection,on_delete=models.CASCADE,related_name='weeks',null=True)
    start_of_week = models.DateField()
    end_of_week = models.DateField()
    week_number = models.PositiveIntegerField()
    academic_week_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)    
    facility_type = models.CharField(max_length=3,null=True,default='C')
    time_period = models.CharField(max_length=5,choices=time_choices,null=True)
    block = models.ForeignKey(ProgarmmeBlock,on_delete=models.SET_NULL,null=True,related_name='cohort_period_weeks')
    file = models.FileField(blank=True,upload_to=update_timetable_path,null=True)


class EducationPlanYearSectionWeekDay(models.Model):
    '''
    education plan Model per day for timetable
    '''
    
    class Meta:
        ordering = ['day']

    CHOICES = (('Demonstration','Demonstration'),('Practice','Practice'))

    
    education_plan_section_week = models.ForeignKey(EducationPlanYearSectionWeeks,on_delete=models.CASCADE,related_name='days')
    day = models.DateField()    
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)



class EducationPlanYearSectionWeekDaySession(models.Model):
    '''
    education plan Model per day for timetable
    '''
    
    class Meta:
        ordering = ['day']

    CHOICES = (('Demonstration','Demonstration'),('Practice','Practice'))

    
    day = models.ForeignKey(EducationPlanYearSectionWeekDay,on_delete=models.CASCADE,related_name='timetable_sessions')
    session = models.ForeignKey(LearningProgrammePeriodTimeTableSession,on_delete=models.CASCADE,related_name='timetable_days',null=True)   
    module = models.ForeignKey(CohortRegistrationPeriodModule,on_delete=models.SET_NULL,related_name='timetable_days',null=True)
    study_unit = models.ForeignKey(LearningProgrammeModuleStudyUnit,on_delete=models.SET_NULL,related_name='timetable_days',null=True)
    procedures = models.ManyToManyField(CohortRegistrationProcedure,related_name='timetable_days')
    type_procedure = models.CharField(max_length=13,choices=CHOICES,null=True,blank=True)
    lecturers = models.ManyToManyField(Staff,related_name='timetable_days')
    created_at = models.DateTimeField(auto_now_add=True)
    credits = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
    def procedure_list(self):
        return ", ".join(self.procedures.values_list('procedure__task', flat=True))
    
    def lecture_list(self):
        return ", ".join(self.lecturers.values_list('first_name', flat=True))