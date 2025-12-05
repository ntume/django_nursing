from django.db import models
import os
import boto3
import uuid
from college.models import CohortRegistrationPeriodModule, CohortRegistrationPeriodModuleFormative, CohortRegistrationProcedure, CohortRegistrationProcedureSummative, CohortRegistrationProcedureSummativeTaskAssessment, CohortRegistrationProcedureTaskAssessment, EducationPlanYearSection, EducationPlanYearSectionWeeks, HealthCareFacility, HealthCareFacilityWard, LearningProgramme, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod, LearningProgrammeModule, LearningProgrammePeriodWILRequirement, Staff
from configurable.models import ClinicalProcedureThemeTask, Country, Disability, Discipline, Gender, Indemnity, Language, NQFLevel, Nationality, ProgarmmeBlock, Province, Race, RegisterCategory, ResidentialStatus, SchoolCodes, ShiftType, Sponsorship, Suburb, TypeOfID, TypeOfLeave, VaccinationDose, Ward
from django.db.models import Sum
from accounts.models import User
from django_nursing import settings
from django_nursing.utility_functions import number_of_days

# Create your models here.


def update_filename(instance, filename):
    path = "profile/"
    ext = filename.split('.')[-1]
    format = "{}.{}".format(instance.id,ext)
    return os.path.join(path, format)


def update_leave_filename(instance, filename):
    path = "student/leave/"
    ext = filename.split('.')[-1]
    format = "{}.{}".format(instance.id,ext)
    return os.path.join(path, format)


def student_registration_document_file_path(instance, filename):
    """generate file path new file"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('students/registration/documents/',filename)


class Student(models.Model):
    '''
    table for the learner list
    '''
    
    CHOICES_AREA = (('Rural','Rural'),('Urban','Urban'))
    CHOICES = (('Yes','Yes'),('No','No'))
    CHOICE_RESIDENCE = (('Permanent Resident','Permanent Resident'),('South Africa','South Africa'),('Dual (SA plus other)','Dual (SA plus other)'),('Temporary Resident','Temporary Resident'),('Non Resident','Non Resident'),('Other','Other'))
    CHOICE_MARITAL = (('Unknown','Unknown'),('Single','Single'),('Married','Married'),('Divorced','Divorced'))
    
    
    student_number = models.CharField(max_length=15,null=True)
    title = models.CharField(max_length=5,null=True)
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50,null=True)  
    maiden_name = models.CharField(max_length=50,null=True)  
    id_number = models.CharField(max_length=20,unique=True)    
    email = models.EmailField(null=True,max_length=100,blank=True)
    cellphone = models.CharField(max_length=20,null=True,blank=True)
    gender = models.ForeignKey(Gender,on_delete=models.SET_NULL,null=True,related_name='learners')
    race = models.ForeignKey(Race,on_delete=models.SET_NULL,null=True,related_name='learners')
    age = models.PositiveIntegerField(null=True)
    disability = models.CharField(max_length=3,default='No')
    disability_specify = models.ForeignKey(Disability,null=True,on_delete=models.SET_NULL)
    disabilities = models.ManyToManyField(Disability,related_name='students')
    highest_nqf_level = models.ForeignKey(NQFLevel,on_delete=models.SET_NULL,null=True,related_name='learners')
    highest_other = models.CharField(max_length=200,null=True)
    language = models.ForeignKey(Language,on_delete=models.SET_NULL,null=True,related_name='learners')
    area = models.ForeignKey(Suburb,on_delete=models.SET_NULL,null=True)
    type_of_area = models.CharField(max_length=5,null=True,choices=CHOICES_AREA)
    employed = models.CharField(max_length=3,choices=CHOICES,null=True)
    marticulated = models.CharField(max_length=3,choices=CHOICES,null=True)
    marticulated_sa = models.CharField(max_length=3,choices=CHOICES,null=True)
    high_school = models.CharField(max_length=150,null=True)
    high_school_code = models.ForeignKey(SchoolCodes,on_delete=models.SET_NULL,null=True,related_name="learners")
    highest_qualification = models.CharField(max_length=200,null=True)
    year_national_certificate = models.CharField(max_length=4,null=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='learners')
    created_at = models.DateTimeField(auto_now_add=True)
    physical_address_1 = models.CharField(max_length=100,blank=True)
    physical_address_2 = models.CharField(max_length=100,blank=True)
    physical_address_3 = models.CharField(max_length=100,blank=True)
    postal_address_1 = models.CharField(max_length=100,blank=True)
    postal_address_2 = models.CharField(max_length=100,blank=True)
    postal_address_3 = models.CharField(max_length=100,blank=True)
    postal_address_postal_code = models.ForeignKey(Suburb,on_delete=models.SET_NULL,null=True,related_name='learners')
    dob = models.DateField(null=True)
    phone_number = models.CharField(max_length=20,null=True,blank=True)
    fax_number = models.CharField(max_length=20,null=True,blank=True)
    province = models.ForeignKey(Province,on_delete=models.SET_NULL,null=True,related_name='learners')
    previous_last_name = models.CharField(max_length=20,null=True)
    residence_status = models.ForeignKey(ResidentialStatus,on_delete=models.SET_NULL,null=True,related_name='learners')
    marital_status = models.CharField(max_length=10,choices=CHOICE_MARITAL,default='Single',null=True)
    otp_request = models.PositiveIntegerField(null=True)
    otp_request_date = models.DateField(null=True)
    nationality = models.ForeignKey(Nationality,on_delete=models.SET_NULL,null=True,related_name='learners')
    type_of_id = models.ForeignKey(TypeOfID,on_delete=models.SET_NULL,null=True,related_name='learners')
    profile_pic = models.ImageField(upload_to=update_filename,default='',null=True)
    bio = models.TextField(null=True)
    on_boarded = models.CharField(max_length=3,default='No',choices=CHOICES)
    preferred_hospital = models.ManyToManyField(HealthCareFacility,related_name='preferred_hospital')
    preferred_phc = models.ManyToManyField(HealthCareFacility,related_name='preferred_phc')
    initials = models.CharField(max_length=4,null=True)
    country_of_issue = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,related_name='student_passports')
    sanc_number = models.PositiveBigIntegerField(null=True)
    indemnity = models.ForeignKey(Indemnity,on_delete=models.SET_NULL,null=True,related_name='students')
    indemnity_number = models.CharField(max_length=20,null=True)
    work_number = models.CharField(max_length=20,null=True,blank=True)
    student_permit_number = models.CharField(max_length=50,null=True)
    student_permit_expiry_date = models.DateField(null=True)
    student_passport_expiry_date = models.DateField(null=True)
    student_card = models.FileField(upload_to=update_filename, null=True, blank=True)

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name
    
    def get_photo_url(self):
        """Ensure the profile picture returns a full URL"""
        if self.profile_pic:
            return f"{settings.MEDIA_URL_AWS}{self.profile_pic.name}"
        return None
    
    
    def get_signed_photo_url(self):
        """Generate a pre-signed URL for private S3 images"""
        if not self.profile_pic:
            return None

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            #region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            signed_url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": self.profile_pic.name,  # Key = S3 object path
                },
                ExpiresIn=3600,  # URL expires in 1 hour
            )
            return signed_url
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None

    def fetch_municipalities(self):
        learner = Student.objects.get(id = self.id)
        surburb = learner.area
        province = surburb.city.district.municipality.province
        return province.municipalities.all()
    
    def fetch_cities(self):
        learner = Student.objects.get(id = self.id)
        surburb = learner.area
        district = surburb.city.district
        return district.cities.all()

    
    def fetch_surburbs(self):
        learner = Student.objects.get(id = self.id)
        surburb = learner.area
        city = surburb.city
        return city.suburbs.all()

    def fetch_schools_province(self):
        learner = Student.objects.get(id = self.id)
        if learner.high_school_code:
            highschool_code = learner.high_school_code
            province = highschool_code.ProvinceCD
            return province.school_codes.all()

    def check_completed_info(self):
        learner = Student.objects.select_related('race','gender','language','area').get(id = self.id)
        completed = True
        reason = "<b>Please complete the following Learner details</b><br>"

        if learner.first_name == "" or learner.first_name == None:
            completed = False
            reason = reason + "Learner First Name<br>"
        
        if learner.last_name == "" or learner.last_name == None:
            completed = False
            reason = reason + "Learner Last Name<br>"
        
        if learner.id_number == "" or learner.id_number == None:
            completed = False
            reason = reason + "Learner ID Number<br>"

        if learner.email == "" or learner.email == None:
            completed = False
            reason = reason + "Learner Email<br>"

        if learner.cellphone == "" or learner.cellphone == None:
            completed = False
            reason = reason + "Learner Cellphone<br>"

        if learner.race == "" or learner.race == None:
            completed = False
            reason = reason + "Learner Race<br>"

        if learner.gender == "" or learner.gender == None:
            completed = False
            reason = reason + "Learner Gender<br>"
        
        if learner.age == "" or learner.age == None:
            completed = False
            
            reason = reason + "Learner Age<br>"

        if learner.language == "" or learner.language == None:
            completed = False
            reason = reason + "Learner Language<br>"        

        if learner.area == "" or learner.area == None:
            completed = False
            reason = reason + "Learner Area<br>"

        if learner.physical_address_1 == "" or learner.physical_address_2 == "" or learner.postal_address_1 == "" or learner.postal_address_2 == ""  :
            completed = False
            
            reason = reason + "Learner Address<br>"

        if learner.type_of_area == "" or learner.type_of_area == None:
            completed = False
            reason = reason + "Learner Type of Area<br>"

        if learner.marticulated == "" or learner.marticulated == None:
            completed = False
            reason = reason + "Learner Marticulation status<br>"

        if learner.marticulated == "Yes" and  learner.marticulated_sa == "":
            completed = False
            reason = reason + "If the learner marticulated from South Africa<br>"
         
        if learner.disability == "Yes" and learner.disability_specify == "" :
            completed = False
            reason = reason + "Learner disability<br>"

        if not hasattr(learner,'next_of_kin'):
            completed = False
            reason = reason + "The learner's next of kin details<br>"

        return completed,reason

    def confirm_completed(self):
        '''
        Return True or False if completed
        '''

        learner = Student.objects.get(id = self.id)
        completed,reason = learner.check_completed_info()
        
        return completed
    





class StudentNextofKin(models.Model):
    '''
    Next of kin of learner
    '''
    
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='next_of_kin')
    type_of_id = models.CharField(max_length=10,default="SA",null=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    id_number = models.CharField(max_length=20)
    home_address = models.TextField()
    postal_address = models.TextField()
    telephone = models.CharField(max_length=20,null=True)
    cellphone = models.CharField(max_length=20,null=True)
    home_number = models.CharField(max_length=20,null=True)
    email = models.CharField(max_length=30,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    relationship = models.CharField(max_length=50,null=True)
    employer = models.CharField(max_length=200,null=True)
    employer_telephone = models.CharField(max_length=10,null=True)
    employer_address = models.TextField(null=True)
    employer_contact_person = models.CharField(max_length=100,null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name
    


class StudentLearningProgramme(models.Model):
    '''
    Student Learning programme
    '''

    
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='learning_programmes')
    learning_programme_cohort = models.ForeignKey(LearningProgrammeCohort,on_delete=models.SET_NULL,null=True,related_name='students')
    learning_programme = models.ForeignKey(LearningProgramme,on_delete=models.CASCADE,related_name='students')
    completed = models.CharField(max_length=3,default='No')
    grade = models.CharField(max_length=10,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    on_boarded = models.CharField(max_length=3,default='No')
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    status = models.CharField(max_length=10,default='Active')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

    def vaccination_dose_1(self):
        return self.vaccinations.filter(vaccine__dose__dose = 'Dose 1').first()

    def vaccination_dose_2(self):
        return self.vaccinations.filter(vaccine__dose__dose = 'Dose 2').first()
    
    def vaccination_dose_3(self):
        return self.vaccinations.filter(vaccine__dose__dose = 'Dose 3').first()
    
    def vaccination_dose_4(self):
        return self.vaccinations.filter(vaccine__dose__dose = 'Booster').first()

    

class StudentLearningProgrammeVaccination(models.Model):
    '''
    Student Learning programme vaccination
    '''
    
    CHOICE_DOSE = (('Dose 1','Dose 1'),('Dose 2','Dose 2'),('Dose 3','Dose 3'),('Booster','Booster'),)

     
    student_learning_programme = models.ForeignKey(StudentLearningProgramme,on_delete=models.CASCADE,related_name='vaccinations')
    vaccine = models.ForeignKey(VaccinationDose,null=True,related_name='vaccinations',on_delete=models.SET_NULL)
    batch_number = models.CharField(max_length=30,null=True,blank=True)
    expiry_date = models.DateField()
    administration_date = models.DateField()
    administration_site = models.CharField(max_length=30,null=True,blank=True)
    administered_by = models.ForeignKey(Staff,on_delete=models.SET_NULL,null=True,related_name='vaccinations')
    next_dose_date = models.DateField(null=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='vaccinations')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


class StudentLearningProgrammeRegistration(models.Model):
    '''
    Student Yearly Registration
    '''
    
    CHOICES = (('Pending','Pending'),('Registered','Registered'))
    
    student_learning_programme = models.ForeignKey(StudentLearningProgramme,on_delete=models.CASCADE,related_name='registrations')
    registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='registrations')
    registration_date = models.DateField(null=True)
    preferred_healthcare_facility = models.ForeignKey(HealthCareFacility,on_delete=models.SET_NULL,null=True,related_name='preferred')
    preferred_clinical_facility = models.ForeignKey(HealthCareFacility,on_delete=models.SET_NULL,null=True,related_name='preferred_clinical')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,default='Pending')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='registrations')
    slug = models.SlugField(unique=True, blank=True)
    pop = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)
    registration_form = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

class StudentLearningProgrammeRegistrationRegister(models.Model):

    '''
    attendance registers for a cohort registration period
    '''

    cohort_registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='registers')
    category = models.ForeignKey(RegisterCategory,on_delete=models.SET_NULL,null=True,related_name='cohorts')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='registers')
    students = models.ManyToManyField(StudentLearningProgrammeRegistration,related_name='registers')
    created_at = models.DateTimeField(auto_now_add=True)


class StudentLearningProgrammeRegistrationSponsor(models.Model):
    '''
    Sponsor
    '''

    CHOICE = (('Self','Self'),('Employer','Employer'))

    
    registration = models.OneToOneField(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='sponsor')
    sponsorship = models.CharField(max_length=10)
    employer_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=50)
    contact_id_number = models.CharField(max_length=50)
    home_phone = models.CharField(max_length=10,null=True)
    cellphone = models.CharField(max_length=10)
    work_phone = models.CharField(max_length=10,null=True)
    relationship = models.CharField(max_length=50)
    physical_address_1 = models.CharField(max_length=100,blank=True)
    physical_address_2 = models.CharField(max_length=100,blank=True)
    physical_address_3 = models.CharField(max_length=100,blank=True)
    postal_address_postal_code = models.ForeignKey(Suburb,on_delete=models.SET_NULL,null=True,related_name='sponsors')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.registration.student_learning_programme.student.first_name
    

class StudentRegistrationModule(models.Model):
    '''
    Student Registration Module Model
    '''

    CHOICES = (
        ('Yes','Yes'),
        ('No','No'),
        ('Pending','Pending'),
    )

    CHOICES_VISITED = (
        ('Pending','Pending'),
        ('Passed','Passed'),
        ('Failed','Failed'),
    )

    registration = models.ForeignKey(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='registered_modules')
    module = models.ForeignKey(CohortRegistrationPeriodModule,on_delete=models.CASCADE,related_name='students',null=True) 
    completed = models.CharField(choices=CHOICES,max_length=7,default='Pending')
    summative_assessor1 = models.DecimalField(decimal_places=1,max_digits=4,null=True)
    summative_assessor2 = models.DecimalField(decimal_places=1,max_digits=4,null=True)
    year_mark = models.DecimalField(decimal_places=1,max_digits=4,null=True)
    final_mark = models.DecimalField(decimal_places=1,max_digits=4,null=True)
    grade = models.CharField(max_length=20,null=True,blank=True)
    moderated = models.CharField(max_length=3,default='No')
    moderater_comment = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    marks_edited_reason = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.registration.student_learning_programme.student.first_name



class StudentRegistrationModuleAssessments(models.Model):
    '''
    Student subject Comments
    '''

    student_registration_module = models.ForeignKey(StudentRegistrationModule,on_delete=models.CASCADE,related_name='assessments')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='assessments')
    assessment = models.ForeignKey(CohortRegistrationPeriodModuleFormative,on_delete=models.SET_NULL,null=True,related_name='assessments')
    marks = models.DecimalField(decimal_places=1,max_digits=4,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.marks



class StudentRegistrationModuleComment(models.Model):
    '''
    Student subject Comments
    '''

    student_registration_module = models.ForeignKey(StudentRegistrationModule,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

class StudentRegistrationModuleEmail(models.Model):
    '''
    Student subject emails
    '''

    student_registration_module = models.ForeignKey(StudentRegistrationModule,on_delete=models.CASCADE,related_name='emails')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='subject_emails')
    title = models.CharField(max_length=50)
    email = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
class StudentLearningProgrammeRegistrationAttachment(models.Model):

    '''
    Attachments for the learners
    '''
     
    student_registration = models.OneToOneField(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='attachments')
    id_copy = models.FileField(upload_to=student_registration_document_file_path,blank=True)
    matric_certificate = models.FileField(upload_to=student_registration_document_file_path,blank=True)
    marriage_certificate = models.FileField(upload_to=student_registration_document_file_path,blank=True)
    other_qualification = models.FileField(upload_to=student_registration_document_file_path,blank=True)
    indemnity = models.FileField(upload_to=student_registration_document_file_path,blank=True)
    sanc_learner_registration = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)
    sanc_certificate = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)
    auxilary_certificate = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)
    practicing_certificate = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)
    saqa_evaluation = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)
    study_permit = models.FileField(upload_to=student_registration_document_file_path,blank=True,null=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)

    def check_completed(self):
        '''
        Check if all attachments are completed
        '''

        completed = True
        reason = "<b>Please make sure to attach the following documents:<br></b>"
         
        attachments = StudentLearningProgrammeRegistrationAttachment.objects.get(id = self.id)
        
        student = attachments.student_registration.student_learning_programme.student

        learning_programme = attachments.student_registration.student_learning_programme.learning_programme


        if not attachments.id_copy:
            completed = False
            reason = reason + "CERTIFIED COPY OF ID/PASSPORT<br>"

        if not attachments.matric_certificate:
            completed = False
            reason = reason + "CERTIFIED COPY OF MATRIC/AFFIDAVIT FOR MATRIC IF THERE IS AN ERROR ON THE MATRIC<br>"
        
        if student.marital_status  == "Married" or student.marital_status  == "Divorced":
            if not attachments.marriage_certificate:
                completed = False
                reason = reason + "CERTIFIED COPY OF MARRIAGE CERT/DECREE OF DIVORCE<br>"
            
        if not attachments.indemnity:
            completed = False
            reason = reason + "PROOF OF INDEMNITY (UNION MEMBERSHIP CARD OR A MEMBERSHIP LETTER/DOCUMENT)<br>"

        if learning_programme.duration > 1: 
            if not attachments.sanc_certificate:
                completed = False
                reason = reason + "CERTIFIED COPY OF SANC CERTIFICATE  OF REGISTRATION AS PRACTITIONER<br>"        

            if attachments.auxilary_certificate:
                pass
            else:
                completed = False
                reason = reason + "CERTIFIED COPY OF ENROLLED OR AUXILIARY CERTIFICATE (COLLEGE OR UNIVERSITY QUALIFICATION)<br>"
        
       
            if attachments.practicing_certificate:
                pass
            else:
                completed = False
                reason = reason + "CERTIFIED COPY OF ANNUAL PRACTICING CERTIFICATE (ALSO KNOWN AS SANC RECEIPT)<br>"

        if student.marticulated_sa == 'No':
            if attachments.saqa_evaluation:
                pass
            else:
                completed = False
                reason = reason + "CERTIFIED COPY SAQA EVALUATION<br>"

        if student.residence_status.status  == "Other" or student.residence_status.status  == "Unknown":   
            if attachments.study_permit:
                pass
            else:
                completed = False
                reason = reason + "CERTIFIED COPY OF STUDY PERMIT<br>"

        return completed,reason


    def confirm_completed(self):
        '''
        Returun True or False if completed
        '''

        attachments = StudentLearningProgrammeRegistrationAttachment.objects.get(id = self.id)
        completed,reason = attachments.check_completed()
        
        return completed
    



class StudentLearningProgrammeRegistrationAttachmentComplianceCheck(models.Model):
    '''
    Compliance checklist
    '''
    learner_programme_attachment = models.OneToOneField(StudentLearningProgrammeRegistrationAttachment,on_delete=models.CASCADE,related_name='compliance') 

    id_copy_compliant = models.CharField(max_length=3,null=True)
    id_copy_comment = models.TextField(null=True)

    marriage_certificate_compliant = models.CharField(max_length=3,null=True)
    marriage_certificate_comment = models.TextField(null=True)

    matric_certificate_compliant = models.CharField(max_length=3,null=True)
    matric_certificate_comment = models.TextField(null=True)

    other_qualification_compliant = models.CharField(max_length=3,null=True)
    other_qualification_comment = models.TextField(null=True)

    indemnity_compliant = models.CharField(max_length=3,null=True)
    indemnity_comment = models.TextField(null=True)

    sanc_learner_registration_compliant = models.CharField(max_length=3,null=True)
    sanc_learner_registration_comment = models.TextField(null=True)

    sanc_certificate_compliant = models.CharField(max_length=3,null=True)
    sanc_certificate_comment = models.TextField(null=True)

    auxilary_certificate_compliant = models.CharField(max_length=3,null=True)
    auxilary_certificate_comment = models.TextField(null=True)

    practicing_certificate_compliant = models.CharField(max_length=3,null=True)
    practicing_certificate_comment = models.TextField(null=True) 

    saqa_evaluation_compliant = models.CharField(max_length=3,null=True)
    saqa_evaluation_comment = models.TextField(null=True)

    study_permit_compliant = models.CharField(max_length=3,null=True)
    study_permit_comment = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)


class StudentRegistrationLeave(models.Model):
    '''
    Student Registration Module Model
    '''

    CHOICES = (
        ('Yes','Yes'),
        ('No','No'),
    )

    CHOICES_APPROVED = (
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected'),
    )

    registration = models.ForeignKey(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='leave_requests')
    type_of_leave = models.ForeignKey(TypeOfLeave,on_delete=models.CASCADE,related_name='students')    
    from_date = models.DateField()
    to_date = models.DateField()
    comment = models.TextField()
    approval_comment = models.TextField(null=True)
    approve_date = models.DateField(null=True)
    approved_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='leave_approvals')
    approved = models.CharField(max_length=10,default='Pending',choices=CHOICES_APPROVED)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=update_leave_filename,default='',null=True)
    number_of_days = models.PositiveIntegerField(default=0)
           
    
    def requested_approved_days(self):
        
        leave_request = StudentRegistrationLeave.objects.get(id = self.id)
        
        count_requested = (StudentRegistrationLeave.
                                   objects.
                                   filter(registration = leave_request.registration,
                                          type_of_leave=leave_request.type_of_leave,
                                          approved='Approved').
                                   aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0 )
                
        
        return count_requested
    
    def remaining_leave_days(self):
        '''
        Function to calculate how many leave days are remaining for the learner
        '''
        
        leave_request = StudentRegistrationLeave.objects.get(id = self.id)
        registration = leave_request.registration
        
        leave_type_breakdown = []
        
        leave_types = TypeOfLeave.objects.all() 

        for leave_type in leave_types:
            remainder_map = {'leave_type':leave_type.type_of_leave}
            count_requested = 0
            count_requested = (StudentRegistrationLeave.
                                objects.
                                filter(registration = registration,
                                        type_of_leave=leave_type,
                                        approved='Approved').
                                aggregate(Sum('number_of_days'))['number_of_days__sum'] or 0 )
            
            count_remainder = leave_type.number_of_days - count_requested

            remainder_map['count_requested'] = count_requested
            remainder_map['count_remainder'] = count_remainder
            remainder_map['total_days'] = leave_type.number_of_days 

            leave_type_breakdown.append(remainder_map)
            
        return leave_type_breakdown


class StudentEducationPlan(models.Model):
    '''
    Student education plan Model
    '''
    
    class Meta:
        ordering = ['education_plan_section_week__academic_week_number'] 

    time_choices = (('Night','Night'),('Day','Day'))
    facility_choices = (('PHC','PHC'),('H','H'),('C','C'))
    
     
    registration = models.ForeignKey(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='education_plans')
    education_plan_section_week = models.ForeignKey(EducationPlanYearSectionWeeks,on_delete=models.CASCADE,related_name='students')
    facility = models.ForeignKey(HealthCareFacility,on_delete=models.SET_NULL,null=True,related_name='students')
    time_period = models.CharField(max_length=5,choices=time_choices,null=True)
    block = models.ForeignKey(ProgarmmeBlock,on_delete=models.SET_NULL,null=True,related_name='student_period_weeks')
    facility_type = models.CharField(max_length=3,null=True)
    discipline = models.ForeignKey(Discipline,on_delete=models.SET_NULL,null=True,related_name='students_master_plan')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)



class StudentEducationPlanSection(models.Model):
    '''
    Student education plan sections
    '''
    
    class Meta:
        ordering = ['education_plan_year_section__start_date'] 

    
    
    registration = models.ForeignKey(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='students_sections')
    education_plan_year_section = models.ForeignKey(EducationPlanYearSection,on_delete=models.CASCADE,related_name='students_sections',null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
    
class StudentEducationPlanSectionWILRequirement(models.Model):
    
    '''
    Student education plan sections wil requirements
    '''
    
    
    student_education_plan_section = models.ForeignKey(StudentEducationPlanSection,on_delete=models.CASCADE,related_name='students_section_wil_requirements')
    period_wil_requirement = models.ForeignKey(LearningProgrammePeriodWILRequirement,on_delete=models.CASCADE,related_name='students_section_wil_requirements')
    hours = models.DecimalField(decimal_places=1,max_digits=4,default=0.0)
    credits = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)



class StudentEducationPlanDay(models.Model):
    '''
    Student education plan Model
    '''
    
    class Meta:
        ordering = ['day']

    CHOICES = (('Off Duty','Off Duty'),('On Duty','On Duty'))

    
    education_plan_section_week = models.ForeignKey(StudentEducationPlan,on_delete=models.CASCADE,related_name='days')
    day = models.DateField()
    ward = models.ForeignKey(Ward,on_delete=models.SET_NULL,null=True,related_name='student_plan_days')
    duty_shift = models.CharField(max_length=10,choices=CHOICES,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


class EmailPreferences(models.Model):

    """
    Stduent Email Preferences
    """

    choice_options = (('Yes','Yes'),('No','No'))

    student = models.OneToOneField(Student,on_delete=models.CASCADE,related_name='email_preferences',primary_key=True,)
    adverts = models.CharField(max_length=3,choices=choice_options,default='No')
    events = models.CharField(max_length=3,choices=choice_options,default='No')
    workshops = models.CharField(max_length=3,choices=choice_options,default='No')
    surveys = models.CharField(max_length=3,choices=choice_options,default='No')

    def __str__(self):
        return "Email Settings added"



class SIMProcedureLog(models.Model):
    '''
    Student Sim procedure log added by lecturer
    '''
    
    class Meta:
        ordering = ['start']
        
    CHOICE_TYPE = (('Demonstration','Demonstration'),('Assessment','Assessment'))
        
    
    start = models.TimeField()
    end = models.TimeField()
    date = models.DateField(null=True)
    procedure = models.ForeignKey(CohortRegistrationProcedure,on_delete=models.SET_NULL,null=True,related_name='sim_logs')
    registration_period = models.ForeignKey(LearningProgrammeCohortRegistrationPeriod,on_delete=models.SET_NULL,null=True,related_name='sim_logs')
    added_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='sim_logs')
    attendance_type = models.CharField(max_length=15,default='Demonstration',choices=CHOICE_TYPE)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    

class StudentLogSheet(models.Model):
    '''
    Student logsheet
    '''
    
    class Meta:
        ordering = ['start']
        
    CHOICES = (('Yes','Yes'),('No','No'))
    
    
    
    registration = models.ForeignKey(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='logsheets')
    shift = models.ForeignKey(ShiftType,on_delete=models.CASCADE,related_name='logsheets',null=True)
    block = models.ForeignKey(ProgarmmeBlock,on_delete=models.SET_NULL,null=True,related_name='logsheets')
    start = models.TimeField()
    end = models.TimeField()
    date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    student_impression = models.PositiveIntegerField(null=True)
    student_comment = models.TextField(blank=True)
    mentor_comment = models.TextField(blank=True)
    mentor_acknowledgment = models.CharField(max_length=3,blank=True,choices=CHOICES)
    competent = models.CharField(max_length=3,blank=True)
    marks = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    procedure = models.ForeignKey(ClinicalProcedureThemeTask,on_delete=models.SET_NULL,null=True,related_name='logsheets')
    cohort_procedure = models.ForeignKey(CohortRegistrationProcedure,on_delete=models.SET_NULL,null=True,related_name='logsheets')
    discipline = models.ForeignKey(Discipline,on_delete=models.SET_NULL,null=True,related_name='logsheets')
    ward = models.ForeignKey(Ward,on_delete=models.SET_NULL,null=True,related_name='logsheets')
    facility_ward = models.ForeignKey(HealthCareFacilityWard,on_delete=models.SET_NULL,null=True,related_name='logsheets')
    hours = models.DecimalField(decimal_places=1,max_digits=4,default=0.0)
    sim_procedure_log = models.ForeignKey(SIMProcedureLog,on_delete=models.SET_NULL,null=True,related_name='logsheets')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
    def fetch_healthcare_facility_wards(self):
        
        entry = StudentLogSheet.objects.get(id = self.id)
        
        education_plan_check = StudentEducationPlan.objects.filter(registration = entry.registration,
                                               education_plan_section_week__start_of_week__lte = entry.date,
                                               education_plan_section_week__end_of_week__gte = entry.date).first()
    
        facility = education_plan_check.facility
        
        wards = None

        if facility:

            wards = facility.wards.all()
        
        return wards
    
class StudentProcedureFormative(models.Model):

    '''
    Student Formative Assessments for a student.
    '''

    registration = models.ForeignKey(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='formative_procedures')    
    created_at = models.DateTimeField(auto_now_add=True)
    cohort_procedure = models.ForeignKey(CohortRegistrationProcedure,on_delete=models.SET_NULL,null=True,related_name='formative_procedures')
    final_mark = models.PositiveIntegerField(null=True, blank=True)

    def update_final_mark(self):
        """
        Updates the final mark based on attempt rules:
        - First attempt: actual mark
        - Second/third attempt: cap at 60% if mark exceeds 60
        """
        latest_attempt = self.formative_attempts.order_by('-attempt').first()
        if latest_attempt:
           
            max_mark = latest_attempt.formative_assessments.aggregate(max_mark=models.Avg('assessor_mark'))['max_mark']
           
            if max_mark is not None:
                if latest_attempt.attempt == 1:
                    self.final_mark = max_mark
                else:
                    self.final_mark = min(max_mark, 60)  # Cap at 60%
                self.save()

class StudentProcedureFormativeAssessmentAttempt(models.Model):

    '''
    Tracks a student's assessment attempts
    '''

    ATTEMPT_CHOICES = [(1, '1st Attempt'), (2, '2nd Attempt'), (3, '3rd Attempt'), (4, 'Special Attempt')]

    created_at = models.DateTimeField(auto_now_add=True)
    attempt = models.PositiveIntegerField(choices=ATTEMPT_CHOICES, default=1)
    cohort_procedure = models.ForeignKey(CohortRegistrationProcedure,on_delete=models.SET_NULL,null=True,related_name='formative_attempts')
    student_procedure_formative = models.ForeignKey(StudentProcedureFormative,on_delete=models.SET_NULL,null=True,related_name='formative_attempts')

    class Meta:
        unique_together = ('student_procedure_formative', 'attempt')  # Ensures max 3 attempts

    def save(self, *args, **kwargs):
        """
        Prevents a student from having more than 4 attempts.
        """
        existing_attempts = StudentProcedureFormativeAssessmentAttempt.objects.filter(
            student_procedure_formative=self.student_procedure_formative
        ).count()
        if existing_attempts >= 4:
            raise ValueError("Maximum of 4 attempts allowed per procedure.")
        super().save(*args, **kwargs)

class StudentProcedureFormativeAssessment(models.Model):

    '''
    Student Formative Assessments
    '''

    start = models.TimeField(null=True)
    end = models.TimeField(null=True)
    date = models.DateField(null=True)
    assessor = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='formative_assessments',null=True)
    assessor_mark = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attempt = models.ForeignKey(StudentProcedureFormativeAssessmentAttempt,on_delete=models.SET_NULL,related_name='formative_assessments',null=True)

    def save(self, *args, **kwargs):
        """
        Updates the final mark when an assessment is saved.
        """
        super().save(*args, **kwargs)
        
        self.attempt.student_procedure_formative.update_final_mark()
    

    
    
class StudentLogSheetAssessment(models.Model):
    '''
    Student logsheet assessment
    '''
    
    CHOICES = (('Competent','Competent'),('Not Yet Competent','Not Yet Competent'),('Not Applicable','Not Applicable'))
    
    
    log_sheet = models.ForeignKey(StudentLogSheet,on_delete=models.CASCADE,related_name='assessment')
    assessment = models.ForeignKey(CohortRegistrationProcedureTaskAssessment,on_delete=models.CASCADE,related_name='assessment')
    answer = models.CharField(max_length=20,choices=CHOICES,blank=True)
    comment = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True) 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    

class StudentProcedureFormativeAssessmentAnswer(models.Model):
    '''
    Student assessment
    '''
    
    CHOICES = (('Competent','Competent'),('Not Yet Competent','Not Yet Competent'),('Not Applicable','Not Applicable'))
    
    
    attempt = models.ForeignKey(StudentProcedureFormativeAssessment,on_delete=models.CASCADE,related_name='assessments')
    assessment = models.ForeignKey(CohortRegistrationProcedureTaskAssessment,on_delete=models.CASCADE,related_name='formative_assessments')
    answer = models.CharField(max_length=20,choices=CHOICES,blank=True)
    comment = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True) 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)


class StudentProcedureSummative(models.Model):

    '''
    Student Summative Assessments
    '''

    registration = models.ForeignKey(StudentLearningProgrammeRegistration,on_delete=models.CASCADE,related_name='summative_procedures')    
    created_at = models.DateTimeField(auto_now_add=True)
    cohort_procedure = models.ForeignKey(CohortRegistrationProcedureSummative,on_delete=models.SET_NULL,null=True,related_name='summative_procedures')
    final_mark = models.PositiveIntegerField(null=True)

    def update_final_mark(self):
        """
        Updates the final mark based on attempt rules:
        - First attempt: actual mark
        - Second attempt: cap at 60% if mark exceeds 60
        """
        latest_attempt = self.summative_attempts.order_by('-attempt').first()
        if latest_attempt:
            max_mark = latest_attempt.summative_assessments.aggregate(max_mark=models.Avg('assessor_mark'))['max_mark']
            if max_mark is not None:
                if latest_attempt.attempt == 1:
                    self.final_mark = max_mark
                else:
                    self.final_mark = min(max_mark, 60)  # Cap at 60%
                self.save()



class StudentProcedureSummativeAssessmentAttempt(models.Model):

    """
    Tracks a student's summative assessment attempts.
    """
    ATTEMPT_CHOICES = [(1, '1st Opportunity'), (2, '2nd Opportunity')]

    created_at = models.DateTimeField(auto_now_add=True)
    attempt = models.PositiveIntegerField(choices=ATTEMPT_CHOICES, default=1)
    cohort_procedure = models.ForeignKey(CohortRegistrationProcedureSummative,on_delete=models.SET_NULL,null=True,related_name='summative_attempts')
    student_procedure_summative = models.ForeignKey(StudentProcedureSummative,on_delete=models.SET_NULL,null=True,related_name='summative_attempts')

    class Meta:
        unique_together = ('student_procedure_summative', 'attempt')  # Ensures max 2 attempts

    def save(self, *args, **kwargs):
        """
        Prevents a student from having more than 2 attempts.
        """
        existing_attempts = StudentProcedureSummativeAssessmentAttempt.objects.filter(
            student_procedure_summative=self.student_procedure_summative
        ).count()
        if existing_attempts >= 2:
            raise ValueError("Maximum of 2 attempts allowed per procedure.")
        super().save(*args, **kwargs)


class StudentProcedureSummativeAssessment(models.Model):

    '''
    Student Summative Assessments
    '''

    attempt_choices = (('1','1'),('2','2'),('3','3'))

    start = models.TimeField(null=True)
    end = models.TimeField(null=True)
    date = models.DateField(null=True)
    assessor = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='summative_assessments',null=True)
    assessor_mark = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attempt = models.ForeignKey(StudentProcedureSummativeAssessmentAttempt,on_delete=models.SET_NULL,related_name='summative_assessments',null=True)

    def save(self, *args, **kwargs):
        """
        Updates the final mark when an assessment is saved.
        """
        super().save(*args, **kwargs)
        self.attempt.student_procedure_summative.update_final_mark()


class StudentProcedureSummativeAssessmentAnswer(models.Model):
    '''
    Student assessment
    '''
    
    CHOICES = (('Competent','Competent'),('Not Yet Competent','Not Yet Competent'),('Not Applicable','Not Applicable'))
    
    
    attempt = models.ForeignKey(StudentProcedureSummativeAssessment,on_delete=models.CASCADE,related_name='assessments')
    assessment = models.ForeignKey(CohortRegistrationProcedureSummativeTaskAssessment,on_delete=models.CASCADE,related_name='summative_assessments')
    answer = models.CharField(max_length=20,choices=CHOICES,blank=True)
    comment = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True) 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)