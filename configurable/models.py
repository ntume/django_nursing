from django.db import models
import uuid

from accounts.models import User

# Create your models here.

class Country(models.Model):

    id = models.PositiveIntegerField(primary_key=True)
    country_code = models.CharField(max_length=5)
    country = models.CharField(max_length=30)

    def __str__(self):
        return self.countryName


class Province(models.Model):

    class Meta:
        ordering = ['province']

    country = models.ForeignKey(Country,on_delete=models.CASCADE,related_name='provinces')
    province = models.CharField(max_length=50)

    def __str__(self):
        return self.province


class Municipality(models.Model):
    '''
    District municipalities
    '''

    class Meta:
        ordering = ['municipality']

    province = models.ForeignKey(Province,on_delete=models.CASCADE,related_name='municipalities')
    municipality = models.CharField(max_length=50)

    def __str__(self):
        return self.municipality


class District(models.Model):

    '''
    Local Municipalities
    '''

    class Meta:
        ordering = ['district']

    district = models.CharField(max_length=50)
    municipality = models.ForeignKey(Municipality,on_delete=models.CASCADE,related_name='districts')
    province = models.ForeignKey(Province,on_delete=models.CASCADE,related_name='districts',null=True)

    def __str__(self):
        return self.district


class City(models.Model):

    class Meta:
        ordering = ['city']

    city = models.CharField(max_length=50)
    district = models.ForeignKey(District,on_delete=models.CASCADE,related_name='cities')

    def __str__(self):
        return self.city


class Suburb(models.Model):

    class Meta:
        ordering = ['postal_code']

    suburb = models.CharField(max_length=50)
    city = models.ForeignKey(City,on_delete=models.CASCADE,related_name='suburbs')
    postal_code = models.CharField(max_length=4)

    def __str__(self):
        return self.suburb


class PostalCodes(models.Model):
    '''
    List of postal codes and suburbs
    '''

    postal_code = models.CharField(max_length=4)
    municipality = models.CharField(max_length=30)
    suburb = models.CharField(max_length=30,null=True)
    district = models.CharField(max_length=30,null=True)
    city = models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.postal_code


class Language(models.Model):
        #language choices
        LANGUAGE_CHOICES = (
            (1,'Afrikaans'),
            (2,'English'),
            (3,'isiNdebele'),
            (4,'isiXhosa'),
            (5,'isiZulu'),
            (6,'Sepedi'),
            (7,'Sesotho'),
            (8,'Setswana'),
            (9,'Sign language'),
            (10,'SiSwati'),
            (11,'Tshivenda'),
            (12,'Xitsonga'),
            (13,'French'),
            (14,'German'),
            (15,'Portuguese'),
            (16,'Other'),
        )

        id = models.AutoField(auto_created = True,
                  primary_key = True,
                  serialize = False, 
                  verbose_name ='ID'
                )
        language = models.CharField(max_length=20)
        code = models.CharField(max_length=5,null=True)

        def __str__(self):
            return self.language


class Gender(models.Model):
    '''
    Gender table to be used in several other apps
    '''

    gender = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=1,null=True)

    def __str__(self):
        return self.gender


class Disability(models.Model):
    '''
    Disability table to be used in several other apps
    '''
    
    disability= models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=2,null=True)

    def __str__(self):
        return self.disability


class EconomicStatus(models.Model):
    '''
    The economic status of an individual e.g employed, unemployed etc..
    '''

    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status


class EmploymentEconomicStatus(models.Model):
    '''
    The economic status of an individual to be used by ETQA
    '''

    status = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=2,null=True)

    def __str__(self):
        return self.status


class Race(models.Model):
    '''
    The race of an individual
    '''

    race = models.CharField(max_length=20)
    code = models.CharField(max_length=3,null=True)

    def __str__(self):
        return self.race


class ResidentialStatus(models.Model):
    '''
    The residential status of an individual
    '''

    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=2,null=True)    


class TypeOfID(models.Model):
    '''
    The type of ID of an individual
    '''

    type_of_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=3,null=True)  
    person = models.CharField(max_length=10,default='external')


class StructureStatusID(models.Model):
    '''
    The structure status ID of an individual
    '''

    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=3,null=True) 


class Industry(models.Model):

    code = models.PositiveIntegerField()
    industry = models.CharField(max_length=100)

    def __str__(self):
        return self.industry
        

class QuestionType(models.Model):

    '''
    The different question types we can ask in all evaluations
    '''

    choices_options = (('Yes','Yes'),('No','No'))

    type = models.CharField(max_length=200)
    options = models.CharField(max_length=3,choices=choices_options,default='Yes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.type


class QuestionTypeOptions(models.Model):

    '''
    The options for the types
    '''

    type = models.ForeignKey(QuestionType,on_delete=models.CASCADE,related_name='type_options')
    option = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.option

    

class AlternateIDType(models.Model):
    '''
    Alternate ID Type table to be used in several other apps
    '''

    CHOICES = (('Person','Person'),('Other','Other'))

    alternate_id_type = models.CharField(max_length=50)
    code = models.CharField(max_length=3,null=True)
    person_type = models.CharField(max_length=6,null=True)

    def __str__(self):
        return self.id_type
    

class Nationality(models.Model):
    '''
    nationality table to be used in several other apps
    '''

    nationality = models.CharField(max_length=50)
    code = models.CharField(max_length=3,null=True)

    def __str__(self):
        return self.nationality
    

class SchoolCodes(models.Model):
    '''
    natemis db for school codes
    '''

    class Meta:
        ordering = ['Official_Institution_Name'] 

    NatEmis = models.PositiveBigIntegerField(null=True)
    province = models.CharField(max_length=50)
    ProvinceCD = models.ForeignKey(Province,null=True,on_delete=models.SET_NULL,related_name = 'school_codes')
    Official_Institution_Name = models.TextField()
    STATUS = models.CharField(max_length=50)
    Type_DoE = models.CharField(max_length=50)
    Phase_PED = models.CharField(max_length=50)
    Specialisation = models.CharField(max_length=50)
    EIDistrict = models.CharField(max_length=50)
    GIS_Long = models.CharField(max_length=50)
    GIS_Lat = models.CharField(max_length=50)
    SP_Code = models.PositiveIntegerField(null=True)
    Urban_Rural = models.CharField(max_length=50)
    OldNATEMIS = models.PositiveIntegerField(null=True)
    NewNATEMIS = models.PositiveIntegerField(null=True)
    Learners = models.PositiveIntegerField(null=True)
    Educators = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.Official_Institution_Name
    

class NQFLevel(models.Model):

    nqf_level = models.PositiveIntegerField()
    description = models.CharField(max_length=100)
    code = models.CharField(max_length=3,null=True)

    def __str__(self):
        return self.description
    
    
class TypeOfLeave(models.Model):

    type_of_leave = models.CharField(max_length=100)
    number_of_days = models.PositiveIntegerField()
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.type_of_leave
    
    
class Indemnity(models.Model):

    indemnity = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.indemnity   
    

class Sponsorship(models.Model):

    sponsorship = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sponsorship   
    
    
class ProgarmmeBlock(models.Model):
    
    block_code = models.CharField(max_length=10)
    block_name = models.CharField(max_length=50)
    wil = models.CharField(max_length=3,default='No')
    internal = models.CharField(max_length=3,default='No')


class Demonstration(models.Model):
    
    
    demonstration = models.CharField(max_length=200)
    duration = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Ward(models.Model):

    ward = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    

class Discipline(models.Model):    
    
    discipline = models.CharField(max_length=200)
    wards = models.ManyToManyField(Ward,related_name='disciplines')
    created_at = models.DateTimeField(auto_now_add=True)
    


    

class ClinicalProcedureTheme(models.Model):
    
    
    theme = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ClinicalProcedureThemeTask(models.Model):
    
    
    theme = models.ForeignKey(ClinicalProcedureTheme,on_delete=models.CASCADE,related_name='tasks')
    task = models.CharField(max_length=200)
    duration = models.DecimalField(decimal_places=2,max_digits=4,default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)


class ClinicalProcedureThemeTaskAssessment(models.Model):
    '''
    procedure assessments
    '''
    
    CHOICES = (('Note','Note'),('Heading','Heading'),('Question','Question'))

    class Meta:
        ordering = ['number']

    task = models.ForeignKey(ClinicalProcedureThemeTask,on_delete=models.CASCADE,related_name='assessments')
    question = models.TextField()
    question_type = models.CharField(max_length=10,choices=CHOICES,default='Question')
    number = models.CharField(max_length=20)
    penalty = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not isinstance(self.number, str):
            self.number = str(self.number)
        self.number = '.'.join(f"{int(part):02}" for part in self.number.split('.'))
        super().save(*args, **kwargs)
        
    @property
    def original_number(self):
        # Remove padding for display
        return '.'.join(str(int(part)) for part in self.number.split('.'))

    def __str__(self):
        # Use the unpadded number for display purposes
        return f"{self.original_number} - {self.name}"
    
    
class ShiftType(models.Model):
    
    
    shift = models.CharField(max_length=100)
    shift_code = models.CharField(max_length=20)
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class WILScaleQuestion(models.Model):
    
    
    question = models.CharField(max_length=200)
    simulated = models.CharField(max_length=3,default='No')
    created_at = models.DateTimeField(auto_now_add=True)
    

class RegistrationBlockCode(models.Model):
    '''
    Registration Block Codes
    '''
    
    code = models.CharField(max_length=5)
    description = models.CharField(max_length=20)


class RegisterCategory(models.Model):
    '''
    Register categories
    '''
    
    category = models.CharField(max_length=30)
    description = models.CharField(max_length=100)


class VaccinationDose(models.Model):
    '''
    Vaccine Doses
    '''
    
    dose = models.CharField(max_length=50)
    
    
