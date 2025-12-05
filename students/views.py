import threading
from django.shortcuts import render,HttpResponse,redirect,Http404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import smart_str
from django.conf import settings
from django.db.models import Sum
from django.core.files import File
from io import BytesIO
import os
import json
import datetime
from wsgiref.util import FileWrapper
from io import StringIO
from zipfile import ZipFile
from django.db.models import Max

from accounts.models import User
from accounts.views import create_user_profile_external, password_gen
from college.models import CohortRegistrationPeriodModule, CohortRegistrationPeriodModuleFormative, EducationPlanYearSection, EducationPlanYearSectionWeeks, HealthCareFacility, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod, LearningProgrammeModuleFormative, LearningProgrammePeriodWILRequirement, Staff
from configurable.models import Country, Disability, Discipline, Gender, NQFLevel, Nationality, ProgarmmeBlock, Province, Race, ResidentialStatus, Suburb, TypeOfID, TypeOfLeave, VaccinationDose, Ward
from django_nursing.email_functions import send_email_general
from students.generate_proof_of_registration import MyPrintProofOfRegistration
from students.print_registration_form import MyPrintRegistrationForm
from .forms import LearnerAddressForm, LearnerAttachementAuxillaryCertificateForm, LearnerAttachementIDForm, LearnerAttachementIndemnityForm, LearnerAttachementMarriageForm, LearnerAttachementMatricForm, LearnerAttachementOtherQualificationForm, LearnerAttachementPracticingCertificateForm, LearnerAttachementSAQAForm, LearnerAttachementSancCertificateForm, LearnerAttachementSancLearnerRegistrationForm, LearnerAttachementStudyPermitForm, LearnerExtendedForm, LearnerNextKinForm, StudentBasicForm, StudentCreateForm, StudentEducationPlanSectionWILRequirementForm, StudentLearningProgrammeVaccinationForm,StudentProfileForm,StudentProfilePicForm, StudentRegistrationLeaveForm
from .models import Student,Language, StudentEducationPlan, StudentEducationPlanDay, StudentEducationPlanSection, StudentEducationPlanSectionWILRequirement, StudentLearningProgramme, StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationAttachment, StudentLearningProgrammeVaccination, StudentNextofKin, StudentRegistrationModule, StudentRegistrationModuleAssessments

from za_id_number.za_id_number import SouthAfricanIdentityValidate,SouthAfricanIdentityNumber

today = datetime.date.today()

# Create your views here.



def generate_student_number() -> str:
    """
    Generates a student number in the format S[Year][Sequence], e.g., S20250001
    """
    current_year = datetime.datetime.now().year
    prefix = f"S{current_year}"

    last_student = Student.objects.filter(student_number__startswith=prefix).aggregate(
        Max('student_number')
    )
    last_number = last_student['student_number__max']

    if last_number:
        last_seq = int(last_number[-5:])
        new_seq = str(last_seq + 1).zfill(5)
    else:
        new_seq = "00001"

    return f"{prefix}{new_seq}"


def learner_programme_details(request,learner_instance):
    '''
    Edit learner information
    '''

    #check ID

    validation_passed = True
    

    if 'type_of_id' in request.POST and request.POST['type_of_id'] == '5':
        
        id_number = request.POST['id_number']
        age = request.POST['age']
        dob = request.POST['dob']
      
        
        gender = Gender.objects.get(id = request.POST['gender'])
        residence_status = ResidentialStatus.objects.get(id = request.POST['residence_status'])
        
        id_validation = SouthAfricanIdentityValidate(id_number)
        if not id_validation.validate():
            validation_passed = False
            messages.warning(request,"Supplied Learner ID Number is not valid, please correct it and resubmit") 
        else:
            #warning checks 
            
            #check age
            id_object = SouthAfricanIdentityNumber(id_number)
     
            if age:
                if age != f'{id_object.age}':
                    messages.warning(request,'Supplied age does not correspond to the ID age calculation')
                    validation_passed = False

            if dob:
                
                if dob != f'{id_object.birthdate}':
                    messages.warning(request,'Supplied date of birth does not correspond to the ID date of birth')
                    validation_passed = False

            if residence_status:
               
                if residence_status.status.lower() != id_object.citizenship.lower():
                    messages.warning(request,'Supplied residency status does not correspond to the ID Number')
                    validation_passed = False

            if gender:
                if gender.gender != id_object.gender:
                    messages.warning(request,'Supplied gender does not correspond to the ID Number')
                    validation_passed = False

    if validation_passed:
    
        form = LearnerExtendedForm(request.POST,instance = learner_instance)
        if form.is_valid():
            learner = form.save(commit = False)
            if 'gender' in request.POST:
                learner.gender_id = request.POST['gender']
            if 'race' in request.POST:
                learner.race_id = request.POST['race']
            if 'language' in request.POST:
                learner.language_id = request.POST['language']
            if 'area' in request.POST:
                learner.area_id = request.POST['area']
            if 'employed' in request.POST:
                learner.employed = request.POST['employed']           
            if 'previous_internship' in request.POST:
                learner.previous_internship = request.POST['previous_internship']
            if 'previous_internship_name' in request.POST:
                learner.previous_internship_name = request.POST['previous_internship_name']
            if 'disability_specify' in request.POST:
                learner.disability_specify_id = request.POST['disability_specify']
            if 'middle_name' in request.POST:
                learner.middle_name = request.POST['middle_name']
            if 'previous_last_name' in request.POST:
                learner.previous_last_name = request.POST['previous_last_name']
            if 'nationality' in request.POST:
                learner.nationality_id = request.POST['nationality']
            if 'type_of_id' in request.POST:
                learner.type_of_id_id = request.POST['type_of_id']
            if 'residence_status' in request.POST:
                learner.residence_status_id = request.POST['residence_status']

            if 'sanc_number' in request.POST and request.POST['sanc_number'] != "":
                learner.sanc_number = request.POST['sanc_number']
            if 'indemnity' in request.POST:
                learner.indemnity_id = request.POST['indemnity']
            if 'indemnity_number' in request.POST:
                learner.indemnity_number = request.POST['indemnity_number']
            if 'student_permit_number' in request.POST:
                learner.student_permit_number = request.POST['student_permit_number']
            if 'student_permit_expiry_date' in request.POST and request.POST['student_permit_expiry_date'] != "":
                learner.student_permit_expiry_date = request.POST['student_permit_expiry_date']
            if 'student_passport_expiry_date' in request.POST and request.POST['student_passport_expiry_date'] != "":
                learner.student_passport_expiry_date = request.POST['student_passport_expiry_date']
            if 'country_of_issue' in request.POST:
                learner.country_of_issue_id = request.POST['country_of_issue']
                
            hospitals = request.POST.getlist('preferred_healthcare_facility_hospital[]')
            for s_id in hospitals:
                hospital = HealthCareFacility.objects.get(id = s_id)
                learner.preferred_hospital.add(hospital)
                
            phcs = request.POST.getlist('preferred_healthcare_facility_phc[]')
            for s_id in phcs:
                phc = HealthCareFacility.objects.get(id = s_id)
                learner.preferred_phc.add(phc)
                
            disabilities = request.POST.getlist('disabilities[]')
            for s_id in disabilities:
                disability = Disability.objects.get(id = s_id)
                learner.disabilities.add(disability)
                    
            learner.save()
            messages.success(request,"Successfully edited learner information")
            return True
        else:
            messages.warning(request,form.errors)
            return False
    else:
        return False


def learner_address_details(request,learner_instance):
    '''
    Edit learner address information
    '''
    
    form = LearnerAddressForm(request.POST,instance = learner_instance)
    if form.is_valid():
        learner = form.save(commit = False)
        if 'email' in request.POST:
            if learner.email:
                if learner.email.lower() != request.POST['email'].lower():
                    check_email_exists = Student.objects.filter(email = request.POST['email']).exists()
                    if check_email_exists:
                        messages.warning(request,'Email address cannot be updated because it is attached to another learner')
                    else:
                        learner.email = request.POST['email']
            else:
                learner.email = request.POST['email']

        if 'physical_address_3' in request.POST:
            learner.physical_address_3 = request.POST['physical_address_3']
        if 'postal_address_3' in request.POST:
            learner.postal_address_3 = request.POST['postal_address_3']
        if 'province' in request.POST:
            learner.province_id = request.POST['province']
        if 'area' in request.POST:
            learner.area_id = request.POST['area']

        if 'postal_address_postal_code' in request.POST:
            learner.postal_address_postal_code_id = request.POST['postal_address_postal_code']
            
        if 'phone_number' in request.POST and request.POST['phone_number'] != "":
            learner.phone_number = request.POST['phone_number']
        if 'fax_number' in request.POST and request.POST['fax_number'] != "":
            learner.fax_number = request.POST['fax_number']
        if 'type_of_area' in request.POST and request.POST['type_of_area'] != "":
            learner.type_of_area = request.POST['type_of_area']
        
        learner.save()
        messages.success(request,"Successfully edited learner address information") 
    else:
        messages.warning(request,form.errors)
  

def learner_education_details(request,learner):
    '''
    Edit learner education information
    '''

    if 'highest_nqf_level' in request.POST:
        learner.highest_nqf_level_id = request.POST['highest_nqf_level']

    if 'highest_other' in request.POST:
        learner.highest_other = request.POST['highest_other']

    if 'highest_qualification' in request.POST:
        learner.highest_qualification = request.POST['highest_qualification']

    if 'high_school' in request.POST:
        learner.high_school = request.POST['high_school']
        
    if 'marticulated' in request.POST:
        learner.marticulated = request.POST['marticulated']
        
    if 'marticulated_sa' in request.POST:
        learner.marticulated_sa = request.POST['marticulated_sa']

    if 'year_national_certificate' in request.POST:
        learner.year_national_certificate = request.POST['year_national_certificate']
        
    if 'high_school_code' in request.POST and request.POST['high_school_code'] != "0"  and request.POST['high_school_code'] != 'Can not find school':
        learner.high_school_code_id = request.POST['high_school_code']
            
    learner.save()        
    messages.success(request,"Successfully edited learner education information")
        

def learner_next_of_kin_details(request,learner_instance,request_method = 'Add',next_of_kin = None):
    '''
    Edit learner next_of_kin or guardian information
    '''

    if request_method == 'Edit':
        form = LearnerNextKinForm(request.POST,instance=next_of_kin)
        if form.is_valid():
            next_of_kin = form.save(commit = False)
            if 'telephone' in request.POST and request.POST['telephone'] != "":
                next_of_kin.telephone = request.POST['telephone']

            if 'relationship' in request.POST and request.POST['relationship'] != "":
                next_of_kin.relationship = request.POST['relationship']
                
            if 'employer' in request.POST and request.POST['employer'] != "":
                next_of_kin.employer = request.POST['employer']
                
            if 'employer_telephone' in request.POST and request.POST['employer_telephone'] != "":
                next_of_kin.employer_telephone = request.POST['employer_telephone']
                
            if 'employer_address' in request.POST and request.POST['employer_address'] != "":
                next_of_kin.employer_address = request.POST['employer_address']
                
            if 'employer_contact_person' in request.POST and request.POST['employer_contact_person'] != "":
                next_of_kin.employer_contact_person = request.POST['employer_contact_person']  
                
            next_of_kin.save()
            messages.success(request,"Successfully edited Next of Kin information")
      
        else:
            messages.warning(request,form.errors)
       
    else:
        form = LearnerNextKinForm(request.POST)
        if form.is_valid():
            next_of_kin = form.save(commit = False)
            next_of_kin.student = learner_instance
            if 'telephone' in request.POST and request.POST['telephone'] != "":
                next_of_kin.telephone = request.POST['telephone']
                
            if 'relationship' in request.POST and request.POST['relationship'] != "":
                next_of_kin.relationship = request.POST['relationship']
                
            if 'employer' in request.POST and request.POST['employer'] != "":
                next_of_kin.employer = request.POST['employer']
                
            if 'employer_telephone' in request.POST and request.POST['employer_telephone'] != "":
                next_of_kin.employer_telephone = request.POST['employer_telephone']
                
            if 'employer_address' in request.POST and request.POST['employer_address'] != "":
                next_of_kin.employer_address = request.POST['employer_address']
                
            if 'employer_contact_person' in request.POST and request.POST['employer_contact_person'] != "":
                next_of_kin.employer_contact_person = request.POST['employer_contact_person']
                
            next_of_kin.save()
            messages.success(request,"Successfully added next of kin information")
      
        else:
            messages.warning(request,form.errors)
     




class CohortLearnerList(LoginRequiredMixin,ListView):
    template_name = 'students/cohort_students.html'
    context_object_name = 'learners'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CohortLearnerList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  StudentLearningProgramme.objects.filter(learning_programme_cohort_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = self.kwargs['pk'])
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        return context
    


class CohortRegistrationPeriodLearnerList(LoginRequiredMixin,ListView):
    template_name = 'students/cohort_registration_students.html'
    context_object_name = 'learners'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CohortLearnerList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  (StudentLearningProgrammeRegistration.
                 objects.
                 filter(registration_period_id = self.kwargs['pk']).
                 only('student__profile_pic',
                      'id',
                      'student__student_number',
                      'student__id_number',
                      'student__first_name',
                      'student__last_name',
                      'student__email',
                      'status',
                      'student__on_boarded',
                      ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        context['learning_programme_cohort'] = learning_programme_cohort_registration_period.learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort_registration_period.learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        return context
    
    
    
@login_required()
def add_learner_programme_cohort(request,pk):
    '''
    function to add learner to cohort
    '''    
    
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:
        
        cohort = LearningProgrammeCohort.objects.get(id = pk)
        check_learner = Student.objects.filter(id_number = request.POST['id_number'])

        if check_learner.exists():
            learner = check_learner.first()
            '''
            check if the learner is active in this cohort programme
            '''
            
            check_learner_cohort = StudentLearningProgramme.objects.filter(student = learner)
            
            if check_learner_cohort.exists():
                messages.warning(request,'Sorry learner already enrolled on this programme')
            
            else:
                lp = StudentLearningProgramme.objects.create(
                    learning_programme = cohort.learning_programme,
                    learning_programme_cohort = cohort,
                    student = learner,
                    start_date = request.POST['start_date'],
                    end_date = request.POST['end_date'],
                )

                messages.success(request,"Successfully added learner to the programme cohort, make sure to complete all his/her forms")
                
                try:    
                    response = send_email_general(
                        learner.student.email,
                        f'{learner.student.first_name} {learner.student.last_name}',
                        f"Added to Learning Programme",
                        f"You have been added to the Learning Programme: {cohort.learning_programme.programme_code}. Log onto SIMS to complete your registration and onboarding",                        
                        ) 
                except Exception as e:
                    print(str(e)) 
        else:
            form = StudentBasicForm(request.POST)
            if form.is_valid():
                learner = form.save(commit = False)
                #student number
                student_number = generate_student_number()
                learner.student_number = student_number
                learner.save()
                
                lp = StudentLearningProgramme.objects.create(
                    learning_programme = cohort.learning_programme,
                    learning_programme_cohort = cohort,
                    student = learner,
                    start_date = request.POST['start_date'],
                    end_date = request.POST['end_date'],
                )


                messages.success(request,"Successfully added learner to the programme, make sure to complete all his/her forms")
                try:    
                    response = send_email_general(
                        learner.learner.email,
                        f'{learner.learner.first_name} {learner.learner.last_name}',
                        "Added to Learning Programme",
                        f"You have been added to the Learning Programme: {cohort.learning_programme.programme_code}. Log onto SIMS to complete your registration and onboarding",   
                        ) 
                except Exception as e:
                    print(str(e)) 
            else:
                messages.warning(request,form.errors)

        return redirect('students:cohort_learners',pk=pk,)
        
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def remove_learner_programme(request,pk,learner_pk):
    '''
    View to remove the learner from the learning programme
    '''

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:

        learner = StudentLearningProgramme.objects.get(id = learner_pk)
        learner.status = "InActive"
        learner.save()
        
        messages.success(request,"Successfully removed learner from the learning programme cohort")
       
        return redirect('students:cohort_learners',pk=pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')





@login_required()
def view_learner_programme(request,pk,page):
    '''
    View to view the learner details in the learning programme
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10):

        lp = StudentLearningProgramme.objects.get(id = pk)
        learning_programme = lp.learning_programme
        learning_programme_cohort = lp.learning_programme_cohort
        race = Race.objects.all()
        gender = Gender.objects.all()
        nqf_levels = NQFLevel.objects.all()
        areas = Suburb.objects.all()
        languages = Language.objects.all()
        countries = Country.objects.all()
        disabilities = Disability.objects.all()
        provinces = Province.objects.all()
        type_of_ids = TypeOfID.objects.all()
        nationalities = Nationality.objects.all()
        residentrial_statuses = ResidentialStatus.objects.all()
       
        '''
        check progress
        '''

        learner_completed,learner_reason = lp.student.check_completed_info()
        #attachments_completed,attachment_reason = False,"Please attach the required documents"

        
        learner_details_page,education_page,parent_page,host_page,training_provider_page,attachments_page,summary_page,address_page = '','','','','','','',''



        if page == 1:
            learner_details_page = 'active'
        if page == 2:
            education_page = 'active'
        if page == 3:
            parent_page = 'active'
        if page == 4:
            host_page = 'active'
        if page == 5:
            training_provider_page = 'active'
        if page == 6:
            attachments_page = 'active'
        if page == 7:
            summary_page = 'active'
        if page == 8:
            address_page = 'active'

        
        #find out the next learner
        if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6):
            learners = list(StudentLearningProgramme.objects
                         .filter(learning_programme_cohort = lp.learning_programme_cohort)
                         .exclude(status = 'InActive'))

            if lp in learners:
                current_index = learners.index(lp)
            else:
                current_index = None

            next_learner = None
            previous_learner = None
      
            if current_index:
                if current_index == 0:
                    previous_learner = None
                    next_index = current_index + 1
                    if next_index < len(learners):
                        next_learner = learners[next_index]

                elif current_index == len(learners) -1:
                    next_learner= None
                    previous_index = current_index - 1
                    if previous_index >= 0:
                        previous_learner = learners[previous_index]
                else:
                    previous_index = current_index - 1
                    if previous_index >= 0:
                        previous_learner = learners[previous_index]

                    next_index = current_index + 1
                    if next_index < len(learners):
                        next_learner = learners[next_index]
                        
        else:
            next_learner,previous_learner,current_index = None,None,None

        if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1):
            template = 'learner_template.html'
        else:
            template = 'learner_learner_template.html'

        return render(request,f'students/learners/{template}',{
            'previous_learner':previous_learner,
            'next_learner':next_learner,
            'current_index':current_index,
            'lp':lp,
            'race':race,
            'gender':gender,
            'nqf_levels':nqf_levels,
            'areas':areas,
            'learner_completed':learner_completed,
            'learner_reason':learner_reason,
            'languages':languages,
            'learner_details_page':learner_details_page,
            'education_page':education_page,
            'parent_page':parent_page,
            'host_page':host_page,
            'training_provider_page':training_provider_page,
            'attachments_page':attachments_page,
            'summary_page':summary_page,
            'address_page':address_page,
            'countries':countries,
            'disabilities':disabilities,
            'provinces':provinces,
            'type_of_ids':type_of_ids,
            'nationalities':nationalities,
            'residentrial_statuses':residentrial_statuses,
            'learning_programme_cohort':learning_programme_cohort,
            'learning_programme':learning_programme,
        })
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_learner_programme_details(request,pk):
    '''
    Edit learner information
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student

        success = learner_programme_details(request,learner_instance)

        
        return render(request,'messages.html')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def edit_learner_address_details(request,pk):
    '''
    Edit learner address information
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student

        learner_address_details(request,learner_instance)
        
        return render(request,'messages.html')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_learner_education_details(request,pk):
    '''
    Edit learner education information
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner = lp.student

        learner_education_details(request,learner)
    
        return render(request,'messages.html')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def add_lp_next_of_kin_details(request,pk,period_pk):
    '''
    Add Next of Kin
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student

        learner_next_of_kin_details(request,learner_instance,'Add',None)
    
        return redirect('students:view_learner_programme_registration',pk=pk,period_pk=period_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
   

@login_required()
def edit_lp_next_of_kin_details(request,pk,period_pk,next_of_kin_pk):
    '''
    edit Next of Kin
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student
        
        next_of_kin = StudentNextofKin.objects.get(id = next_of_kin_pk)

        learner_next_of_kin_details(request,learner_instance,'Edit',next_of_kin)
    
        return redirect('students:view_learner_programme_registration',pk=pk,period_pk=period_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
 
@login_required()
def delete_lp_next_of_kin_details(request,pk,period_pk,next_of_kin_pk):
    '''
    Add Next of Kin
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student
        next_of_kin = StudentNextofKin.objects.get(id = next_of_kin_pk)
        
        if learner_instance.next_of_kin.count() > 1:
            next_of_kin.delete()
            messages.success(request,'Successfully deleted Next of Kin')
        else:
            messages.warning(request,"You need to have at least one Next of Kin contact details")
    
        return redirect('students:view_learner_programme_registration',pk=pk,period_pk=period_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def edit_learner_next_of_kin_details(request,pk):
    '''
    Edit learner parent or guardian information
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student

        learner_next_of_kin_details(request,learner_instance)

        return render(request,'messages.html')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def check_learner_form_details(request,pk):
    '''
    check learner form
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        lp = StudentLearningProgramme.objects.get(id = pk)

        learner_completed,learner_reason = lp.student.check_completed_info()
        attachments_completed,attachment_reason = False,"Please attach the required documents"

        messages.success(request,'Successfully checked form, please see results below')

        
        return render(request,'students/learners/partials/summary_page.html',{
            'lp':lp,
            'learner_completed':learner_completed,
            'attachments_completed':attachments_completed,
            'attachment_reason':attachment_reason,
            'learner_reason':learner_reason})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



class CohortLearnerVaccinationList(LoginRequiredMixin,ListView):
    template_name = 'students/cohort_student_vaccination.html'
    context_object_name = 'vaccines'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CohortLearnerVaccinationList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  StudentLearningProgrammeVaccination.objects.filter(student_learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = StudentLearningProgramme.objects.get(id = self.kwargs['pk'])
        context['learning_programme_cohort'] = student.learning_programme_cohort
        context['learning_programme'] = student.learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['student'] = student
        context['staffs'] = Staff.objects.all()
        context['doses'] = VaccinationDose.objects.all()
        return context



@login_required()
def add_learner_programme_cohort_student_vaccination(request,pk):
    '''
    function to add learner to cohort
    '''    
    
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:
        
        student = StudentLearningProgramme.objects.get(id = pk)

        #check if dose exists
        check_dose = StudentLearningProgrammeVaccination.objects.filter(vaccine_id = request.POST['vaccine'],student_learning_programme=student).exists()

        if check_dose:
            messages.warning(request,'Dose has already been captured, please select the correct dose')
        else:
            form = StudentLearningProgrammeVaccinationForm(request.POST)
            if form.is_valid():
                dose = form.save(commit = False)
                dose.student_learning_programme = student
                dose.administered_by_id = request.POST['administered_by']
                if 'next_dose_date' in request.POST:
                    dose.next_dose_date = request.POST['next_dose_date']
                if 'vaccine' in request.POST:
                    dose.vaccine_id = request.POST['vaccine']
                dose.user = request.user
                dose.save()
                messages.success(request,"Successfully added vaccination dose")            
            else:
                messages.warning(request,form.errors)

        return redirect('students:cohort_learner_vaccinations',pk=pk,)
        
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def edit_learner_programme_cohort_student_vaccination(request,pk,dose_pk):
    '''
    Edit Dose
    '''    
    
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:
        
        student = StudentLearningProgramme.objects.get(id = pk)
        dose = StudentLearningProgrammeVaccination.objects.get(id = dose_pk)
        form = StudentLearningProgrammeVaccinationForm(request.POST,instance=dose)
        if form.is_valid():
            dose = form.save(commit = False)
            dose.administered_by_id = request.POST['administered_by']
            if 'next_dose_date' in request.POST:
                dose.next_dose_date = request.POST['next_dose_date']
            if 'vaccine' in request.POST:
                dose.vaccine_id = request.POST['vaccine']
            dose.save()
            messages.success(request,"Successfully edited vaccination dose")            
        else:
            messages.warning(request,form.errors)

        return redirect('students:cohort_learner_vaccinations',pk=pk)
        
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def delete_learner_programme_cohort_student_vaccination(request,pk,dose_pk):
    '''
    Delete Dose
    '''

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:

        dose = StudentLearningProgrammeVaccination.objects.get(id = dose_pk)
        dose.delete()
        
        messages.success(request,"Successfully removed Dose")
       
        return redirect('students:cohort_learner_vaccinations',pk=pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')




class CohortAllLearnersVaccinationsList(LoginRequiredMixin,ListView):
    template_name = 'students/cohort_all_students_vaccination.html'
    context_object_name = 'learners'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CohortAllLearnersVaccinationsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  StudentLearningProgramme.objects.filter(learning_programme_cohort_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = self.kwargs['pk'])
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        return context
    

@login_required()
def view_learner_programme_registration(request,pk,period_pk):
    '''
    View to view the learner details in the learning programme
    '''

    if (request.user.logged_in_role_id == 2 or 
        request.user.logged_in_role_id == 1 or 
        request.user.logged_in_role_id == 10 or 
        request.user.logged_in_role_id == 6):

        lp = StudentLearningProgramme.objects.get(id = pk)
        learning_programme = lp.learning_programme
        learning_programme_cohort = lp.learning_programme_cohort
        registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = period_pk)
        
        learner_registration = None
        learner_registration_check = lp.registrations.filter(registration_period = registration_period)
        if learner_registration_check.exists():
            learner_registration = learner_registration_check.first()
        else:
            learner_registration = StudentLearningProgrammeRegistration.objects.create(
                student_learning_programme = lp,
                registration_period = registration_period,
            )
            
        race = Race.objects.all()
        gender = Gender.objects.all()
        nqf_levels = NQFLevel.objects.all()
        areas = Suburb.objects.all()
        languages = Language.objects.all()
        countries = Country.objects.all()
        disabilities = Disability.objects.all()
        provinces = Province.objects.all()
        type_of_ids = TypeOfID.objects.all()
        nationalities = Nationality.objects.all()
        residentrial_statuses = ResidentialStatus.objects.all()
        hc_facilities = HealthCareFacility.objects.filter(category = 'Hospital')
        clinical_facilities = HealthCareFacility.objects.filter(category = 'Primary Health Care')
        
        timetable = None
       
        '''
        check progress
        '''

        learner_completed,learner_reason = lp.student.check_completed_info()
        
        if hasattr(learner_registration,'attachments'):
            attachments_completed,attachment_reason = learner_registration.attachments.check_completed()
        else:
            StudentLearningProgrammeRegistrationAttachment.objects.create(student_registration = learner_registration)
            attachments_completed,attachment_reason = False,"Please attach the required documents"

        submission_complete = False
        if learner_completed and attachments_completed and learner_registration.registered_modules.count() > 0:
            submission_complete = True  
        
        learner_details_page,education_page,parent_page,host_page,training_provider_page,attachments_page,summary_page,address_page = '','','','','','','',''

        
        #find out the next learner
        if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6):
            learners = list(StudentLearningProgramme.objects
                         .filter(learning_programme_cohort = lp.learning_programme_cohort)
                         .exclude(status = 'InActive'))

            if lp in learners:
                current_index = learners.index(lp)
            else:
                current_index = None

            next_learner = None
            previous_learner = None
      
            if current_index:
                if current_index == 0:
                    previous_learner = None
                    next_index = current_index + 1
                    if next_index < len(learners):
                        next_learner = learners[next_index]

                elif current_index == len(learners) -1:
                    next_learner= None
                    previous_index = current_index - 1
                    if previous_index >= 0:
                        previous_learner = learners[previous_index]
                else:
                    previous_index = current_index - 1
                    if previous_index >= 0:
                        previous_learner = learners[previous_index]

                    next_index = current_index + 1
                    if next_index < len(learners):
                        next_learner = learners[next_index]
                        
        else:
            next_learner,previous_learner,current_index = None,None,None

        if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1  or request.user.logged_in_role_id == 6):
            template = 'learner_registration_template.html'
        else:
            template = 'learner_learner_template.html'


        #completed modules
        
        modules = registration_period.modules.all()
        
        module_list = []
        for module in modules:
            #check if learner has completed the module
            map_module = {'module':module}
            check_module = (StudentRegistrationModule.
                            objects.
                            filter(registration__student_learning_programme__student = lp.student,
                                   module = module).
                            exclude(completed = 'Failed'))
            
            if check_module.exists():
                map_module['registered'] = 'Yes'
                map_module['module_registration'] = check_module.first()
            else:
                map_module['registered'] = 'No'
                map_module['module_registration'] = None
                
            module_list.append(map_module)
            
        if request.user.logged_in_role_id == 10:
            timetable = learner_registration.education_plans.all()      

        #check if learner has a user profile
        profile_activated = False
        if learner_registration.student_learning_programme.student.user:
            profile_activated = True          
                                        

        return render(request,f'students/learners/{template}',{
            'previous_learner':previous_learner,
            'next_learner':next_learner,
            'current_index':current_index,
            'lp':lp,
            'race':race,
            'gender':gender,
            'nqf_levels':nqf_levels,
            'areas':areas,
            'learner_completed':learner_completed,
            'learner_reason':learner_reason,
            'languages':languages,
            'learner_details_page':learner_details_page,
            'education_page':education_page,
            'parent_page':parent_page,
            'host_page':host_page,
            'training_provider_page':training_provider_page,
            'attachments_page':attachments_page,
            'summary_page':summary_page,
            'address_page':address_page,
            'countries':countries,
            'disabilities':disabilities,
            'provinces':provinces,
            'type_of_ids':type_of_ids,
            'nationalities':nationalities,
            'residentrial_statuses':residentrial_statuses,
            'learning_programme_cohort':learning_programme_cohort,
            'learning_programme':learning_programme,
            'learner_registration':learner_registration,
            'module_list':module_list,
            'attachments_completed':attachments_completed,
            'attachment_reason':attachment_reason,
            'submission_complete':submission_complete,
            'hc_facilities':hc_facilities,
            'clinical_facilities':clinical_facilities,
            'registration_period':registration_period,
            'today':today,
            'timetable':timetable,
            'profile_activated':profile_activated,
        })
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def learner_programme_registration_module_add(request,pk,registration_pk,module_pk):
    '''
    Edit learner information
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student
        learning_programme = lp.learning_programme
        learning_programme_cohort = lp.learning_programme_cohort
        learner_registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        
        #check if module registration exists
        check_module = (StudentRegistrationModule.objects.
                        filter(registration = learner_registration,module = module_pk).
                        exclude(completed='Failed'))
        
        if not check_module.exists():
            
            module_to_add = CohortRegistrationPeriodModule.objects.get(id = module_pk)            
            
            #check if prerequisite is done
            
            prerequisites = module_to_add.module.prerequisites.all()
            
            prequisites_done = True
            
            for m in prerequisites:
                check_if_done = (StudentRegistrationModule.
                                 objects.
                                 filter(registration = learner_registration,
                                        module__module = m.prerequisite,
                                        completed='Yes').exists())
                
                if not check_if_done:
                    prequisites_done = False
                    messages.warning(request,f'Pre-requisite: {m.prerequisite.module_code} not completed')
            
            
            if prequisites_done:
                registration_module = StudentRegistrationModule.objects.create(registration = learner_registration,
                                                        module = module_to_add)
                
                #delete the assessments
                StudentRegistrationModuleAssessments.objects.filter(student_registration_module = registration_module,marks__isnull = True).delete()
                #check if any assessments exist for the module and add them
                assessments = CohortRegistrationPeriodModuleFormative.objects.filter(module = registration_module.module)
                for assessment in assessments:
                    StudentRegistrationModuleAssessments.objects.create(
                        student_registration_module = registration_module,
                        assessment = assessment,
                    )
                
                messages.success(request,'Successfully added module to registration')
        else:
            messages.warning(request,"Student is still registered for the module")
            
        
        #completed modules
        
        modules = learner_registration.registration_period.modules.all()
        
        module_list = []
        for module in modules:
            #check if learner has completed the module
            map_module = {'module':module}
            check_module = (StudentRegistrationModule.
                            objects.
                            filter(registration__student_learning_programme__student = lp.student,
                                   module = module).
                            exclude(completed = 'Failed'))
            
            if check_module.exists():
                map_module['registered'] = 'Yes'
                map_module['module_registration'] = check_module.first()
            else:
                map_module['registered'] = 'No'
                map_module['module_registration'] = None
                
            module_list.append(map_module) 
        
        return render(request,'students/learners/partials/module_registration_page.html',{'module_list':module_list,
                                               'lp':lp,
                                               'learner_registration':learner_registration})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def learner_programme_registration_module_remove(request,pk,registration_pk,module_pk):
    '''
    Edit learner information
    '''

    if (request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6):
        
        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_instance = lp.student
        learning_programme = lp.learning_programme
        learning_programme_cohort = lp.learning_programme_cohort
        learner_registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        
        try:
            check_module = StudentRegistrationModule.objects.get(id = module_pk)
            if check_module.completed != 'Pending':
                messages.success(request,f'You cannot remove a module that is {check_module.completed}')
            else:
                check_module.delete()
                messages.success(request,'Successfully removed module')
                
        except Exception as e:
            messages.warning(request,str(e))
            
        #completed modules
        
        modules = learner_registration.registration_period.modules.all()
        
        module_list = []
        for module in modules:
            #check if learner has completed the module
            map_module = {'module':module}
            check_module = (StudentRegistrationModule.
                            objects.
                            filter(registration__student_learning_programme__student = lp.student,
                                   module = module).
                            exclude(completed = 'Failed'))
            
            if check_module.exists():
                map_module['registered'] = 'Yes'
                map_module['module_registration'] = check_module.first()
            else:
                map_module['registered'] = 'No'
                map_module['module_registration'] = None
                
            module_list.append(map_module) 
        
        return render(request,'students/learners/partials/module_registration_page.html',{'module_list':module_list,
                                               'lp':lp,
                                               'learner_registration':learner_registration})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

def learner_attachment_bulk_upload(request,pk,registration_pk):
    '''
    save learner attachments
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6:

        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        learning_programme = lp.learning_programme
        
        if hasattr(learner_registration,'attachments'):
            attachment = learner_registration.attachments        
        else:
            attachment = StudentLearningProgrammeRegistrationAttachment.objects.create(student_registration = learner_registration)


            
        if 'id_copy' in request.FILES:
            form_id = LearnerAttachementIDForm(request.POST,request.FILES,instance=attachment)
            if form_id.is_valid():
                form_id.save()
                messages.success(request,"ID Copy attached successfully")
            else:
                messages.warning(request,form_id.errors)


        if 'matric_certificate' in request.FILES:
            form_matric = LearnerAttachementMatricForm(request.POST,request.FILES,instance=attachment)
            if form_matric.is_valid():
                form_matric.save()
                messages.success(request,"Matric certificate attached successfully")
            else:
                messages.warning(request,form_matric.errors)


        if 'sanc_learner_registration' in request.FILES:
            form_affidavit = LearnerAttachementSancLearnerRegistrationForm(request.POST,request.FILES,instance=attachment)
            if form_affidavit.is_valid():
                form_affidavit.save()
                messages.success(request,"SANC LEARNER REGISTRATION FORM attached successfully")
            else:
                messages.warning(request,form_affidavit.errors)

        if 'marriage_certificate' in request.FILES:
            form = LearnerAttachementMarriageForm(request.POST,request.FILES,instance=attachment)
            if form.is_valid():
                form.save()
                messages.success(request,"CERTIFIED COPY OF MARRIAGE CERT/DECREE OF DIVORCE")
            else:
                messages.warning(request,form.errors)

        
        if 'other_qualification' in request.FILES:
            form_fees = LearnerAttachementOtherQualificationForm(request.POST,request.FILES,instance=attachment)
            if form_fees.is_valid():
                form_fees.save()
                messages.success(request,"CERTIFIED COPIES OF OTHER QUALIFICATIONS (MEDICAL: NURSING, FIRST AID, CPR, OTHER: COMPUTERS, ETC.) attached successfully")
            else:
                messages.warning(request,form_fees.errors)


        if 'indemnity' in request.FILES:
            form_reg = LearnerAttachementIndemnityForm(request.POST,request.FILES,instance=attachment)
            if form_reg.is_valid():
                form_reg.save()
                messages.success(request,"PROOF OF INDEMNITY (UNION MEMBERSHIP CARD OR A MEMBERSHIP LETTER/DOCUMENT) attached successfully")
            else:
                messages.warning(request,form_reg.errors)


        if 'sanc_certificate' in request.FILES:
            form_prof = LearnerAttachementSancCertificateForm(request.POST,request.FILES,instance=attachment)
            if form_prof.is_valid():
                form_prof.save()
                messages.success(request,"CERTIFIED COPY OF SANC CERTIFICATE  OF REGISTRATION AS PRACTITIONER  attached successfully")
            else:
                messages.warning(request,form_prof.errors)


        if 'auxilary_certificate' in request.FILES:
            form_contract = LearnerAttachementAuxillaryCertificateForm(request.POST,request.FILES,instance=attachment)
            if form_contract.is_valid():
                form_contract.save()
                messages.success(request,"ECERTIFIED COPY OF ENROLLED OR AUXILIARY CERTIFICATE (COLLEGE OR UNIVERSITY QUALIFICATION) attached successfully")
            else:
                messages.warning(request,form_contract.errors)

        if 'practicing_certificate' in request.FILES:
            form_academic_record = LearnerAttachementPracticingCertificateForm(request.POST,request.FILES,instance=attachment)
            if form_academic_record.is_valid():
                form_academic_record.save()
                messages.success(request,"CERTIFIED COPY OF ANNUAL PRACTICING CERTIFICATE (ALSO KNOWN AS SANC RECEIPT) attached successfully")
            else:
                messages.warning(request,form_academic_record.errors)

        if 'saqa_evaluation' in request.FILES:
            form_placement_letter = LearnerAttachementSAQAForm(request.POST,request.FILES,instance=attachment)
            if form_placement_letter.is_valid():
                form_placement_letter.save()
                messages.success(request,"CERTIFIED COPY SAQA EVALUATION attached successfully")
            else:
                messages.warning(request,form_placement_letter.errors)

        if 'study_permit' in request.FILES:
            form = LearnerAttachementStudyPermitForm(request.POST,request.FILES,instance=attachment)
            if form.is_valid():
                form.save()
                messages.success(request,"CERTIFIED COPY OF STUDY PERMIT attached successfully")
            else:
                messages.warning(request,form.errors)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    return render(request,'students/learners/partials/attachments.html',
                  {'learner':lp,
                   'lp':lp,
                   'learner_registration':learner_registration,
                   'learning_programme':learning_programme,})


@login_required()
def check_learner_registration_form_details(request,pk,registration_pk):
    '''
    check learner form
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6:

        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        

        learner_completed,learner_reason = lp.student.check_completed_info()
        attachments_completed,attachment_reason = learner_registration.attachments.check_completed()
        
        submission_complete = False
        if learner_completed and attachments_completed and learner_registration.registered_modules.count() > 0:
            submission_complete = True

        messages.success(request,'Successfully checked form, please see results below')

        hc_facilities = HealthCareFacility.objects.all()
        return render(request,'students/learners/partials/summary_reg_page.html',{
            'lp':lp,
            'learner_registration':learner_registration,
            'learner_completed':learner_completed,
            'attachments_completed':attachments_completed,
            'attachment_reason':attachment_reason,
            'learner_reason':learner_reason,
            'submission_complete':submission_complete,
            'hc_facilities':hc_facilities})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def learner_registration_form_submit(request,pk,registration_pk):
    
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10 or request.user.logged_in_role_id == 6:

        lp = StudentLearningProgramme.objects.get(id = pk)
        learner_registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        learner_registration.status = 'Registered'
        learner_registration.preferred_healthcare_facility_id = request.POST['preferred_healthcare_facility']
        learner_registration.preferred_clinical_facility_id = request.POST['preferred_clinical_facility']
        learner_registration.registration_date = request.POST['registration_date']
        learner_registration.save()

        create_profile = request.POST.get("create_profile")
        if create_profile == 'on':
            password = password_gen(5)
            success,message = create_user_profile_external(learner_registration.student_learning_programme.student,10,password)
            messages.success(request,message)

        messages.success(request,'Successfully registered student for the period')
        
        #POP
        
        ar = MyPrintProofOfRegistration(f"{learner_registration.id}.pdf", 'A4')        
        
        filename = ar.print_pop(learner_registration)  

        file_path = os.path.join(settings.MEDIA_ROOT, filename)    
        
        with open(file_path, "rb") as file_object:
            file_m3u8 = File(name='pop.pdf', file=file_object)        
            learner_registration.pop.save('pop.pdf', file_m3u8)
            
        
        reg_form = MyPrintRegistrationForm(f"{learner_registration.id}.pdf", 'A4')        
        
        reg_form_filename = reg_form.print_registration_form(learner_registration)  

        file_path = os.path.join(settings.MEDIA_ROOT, reg_form_filename)    
        
        with open(file_path, "rb") as file_object:
            file_m3u8 = File(name='registration_form.pdf', file=file_object)        
            learner_registration.registration_form.save('registration_form.pdf', file_m3u8)
        
        return redirect('students:view_learner_programme_registration',pk=pk,period_pk=learner_registration.registration_period_id)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')




@login_required()
def learning_programme_cohort_registrations(request,pk,period_pk):
    
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = pk)
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = period_pk)
        students = learning_programme_cohort.students.all()
        
        student_list = []
        
        for student in students:
            map_student = {'student':student}
            #check if registration exists
            check_registration = StudentLearningProgrammeRegistration.objects.filter(student_learning_programme = student,
                                                                                     registration_period_id = period_pk)
            if check_registration.exists():
                map_student['registration_details'] = check_registration.first()
            else:
                map_student['registration_details'] = None
                
            student_list.append(map_student)

                
        return render(request,'students/period_registered_students.html',{'students':student_list,
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'cohort_menu':'--active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def students_wil_logsheet_hours(request,pk,period_pk):
    '''
    WIL Logsheet hours
    '''

    if request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1:
        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = pk)
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = period_pk)
        registrations = learning_programme_cohort_period.registrations.all()
        disciplines = Discipline.objects.all()
        wards = Ward.objects.all()

        students = []

        for registration in registrations:

            student_map = {'registration':registration}

            wil_hours = StudentEducationPlanSectionWILRequirement.objects.filter(student_education_plan_section__registration = registration)
            
            logsheets = registration.logsheets.all()
            

            plan_year_section = None

            #find out what section we are in
            plan_year_section_check = EducationPlanYearSection.objects.filter(start_date__lte = today, 
                                                                        end_date__gte = today,
                                                                        education_plan_year__cohort_registration_period = registration.registration_period)
            if plan_year_section_check.exists():
                plan_year_section = plan_year_section_check.first()

            discipline_hours = []
            ward_hours = []

            #check the discipline hours captured and summarize the information
            for d in disciplines:
                discipline_map = {'discipline':d}        
                #check if there are any hours captured
                discipline_map['hours'] = logsheets.filter(discipline = d).aggregate(Sum('hours'))['hours__sum'] or 0
                discipline_map['total_quarter_hours'] = logsheets.filter(discipline = d,
                                                                        date__gte = plan_year_section.start_date,
                                                                        date__lte=plan_year_section.end_date).aggregate(Sum('hours'))['hours__sum'] or 0
                #check required hours
                discipline_map['total_required_hours'] = wil_hours.filter(period_wil_requirement__discipline = d).aggregate(Sum('hours'))['hours__sum'] or 0
                discipline_map['total_required_quarter_hours'] = wil_hours.filter(period_wil_requirement__discipline = d,student_education_plan_section__education_plan_year_section = plan_year_section).aggregate(Sum('hours'))['hours__sum'] or 0
                discipline_hours.append(discipline_map)

            for w in wards:
                ward_map = {'ward':w}
                #check if there are any hours captured
                ward_map['hours'] = logsheets.filter(ward = w).aggregate(Sum('hours'))['hours__sum'] or 0
                ward_hours.append(ward_map)

            student_map['ward_hours'] = ward_hours

            student_map['discipline_hours'] = discipline_hours

            students.append(student_map)

        
        return render(request,
                      'students/period_registered_students_logsheet_hours.html',
                      { 'ward_hours':ward_hours,
                        'discipline_hours':discipline_hours,
                        'registrations':registrations,
                        'students':students,
                        'wards':wards,
                        'disciplines':disciplines,
                        'learning_programme_cohort':learning_programme_cohort,
                        'learning_programme':learning_programme,
                        'learning_programme_cohort_period':learning_programme_cohort_period,
                        'cohort_menu':'--active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class BackgroundThreadSendLearnerRequest(threading.Thread):
    
    def __init__(self,request,students):
        threading.Thread.__init__(self)
        self.students = students
        self.request = request
        

    def run(self):

        for learner in self.students:

            title = "Request to complete AHC SIMS onboarding"
            email_body = f'''You have been added to AHC Student Information Management System (SIMS).
                            Please follow the link below to complete your onboarding process As Soon As Possible.
                            https://nursing.elevatelearn.co.za/api/student/{learner.id}/{learner.student.slug}/onboarding/1'''
           
            send_email_general(
                learner.student.email,
                f'{learner.student.first_name} {learner.student.last_name}',
                title,
                email_body) 
            
@login_required()
def request_group_on_boarding(request,pk):
    
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = pk)
        
        students = learning_programme_cohort.students.filter(student__on_boarded = 'No')
        
        BackgroundThreadSendLearnerRequest(request,students).start()   
        
        messages.success(request,'An email will be sent to all learners to complete the onboarding process')    

                
        return redirect('students:cohort_learners',pk=pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def view_learner_educational_plan_sections(request,pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        lp = registration.student_learning_programme
        registration_period = registration.registration_period
        sections = EducationPlanYearSection.objects.filter(education_plan_year__cohort_registration_period = registration_period)
        
        wil_requirements = LearningProgrammePeriodWILRequirement.objects.filter(period = registration_period.period)
        
        #check if the sections are there for the learner, if not then add it
                
        for section in sections:
            #check if section exists, if not add it
            check_section = StudentEducationPlanSection.objects.filter(registration=registration,
                                                                       education_plan_year_section=section)
            
            if not check_section.exists():
                StudentEducationPlanSection.objects.create(registration=registration,
                                                                       education_plan_year_section=section)
            
        student_sections = StudentEducationPlanSection.objects.filter(registration=registration)
        
        return render(request,'students/learner_education_plan_sections_wil_requirements.html',{
            'registration':registration,
            'lp':lp,
            'wil_requirements':wil_requirements,
            'student_sections':student_sections,
            'cohort_menu':'--active',
        })
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def view_learner_educational_plan_sections_add_wil_requirement(request,pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        section = StudentEducationPlanSection.objects.get(id = pk)
        
        #check if entry exists
        
        check_wil = StudentEducationPlanSectionWILRequirement.objects.filter(student_education_plan_section = section,
                                                                             period_wil_requirement_id = request.POST['period_wil_requirement']).exists()
        
        if not check_wil:
            form = StudentEducationPlanSectionWILRequirementForm(request.POST)
            if form.is_valid():
                wil = form.save(commit = False)
                wil.student_education_plan_section = section
                wil.period_wil_requirement_id = request.POST['period_wil_requirement']
                wil.save()
                
                messages.success(request,'Successfully saved wil requirement')
            else:
                messages.warning(request,form.errors)
            
        else:
            messages.warning(request,'WIL Requirement extsts')
            
        return redirect('students:view_learner_educational_plan_sections',pk=section.registration_id)
            
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def view_learner_educational_plan_sections_edit_wil_requirement(request,pk,wil_pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        section = StudentEducationPlanSection.objects.get(id = pk)
        wil = StudentEducationPlanSectionWILRequirement.objects.get(id = wil_pk)
        
        #check if entry exists
        
        
        form = StudentEducationPlanSectionWILRequirementForm(request.POST,instance=wil)
        if form.is_valid():
            form.save()
            messages.success(request,'Successfully edited wil requirement')
        else:
            messages.warning(request,form.errors)
        
        return redirect('students:view_learner_educational_plan_sections',pk=section.registration_id)
            
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def view_learner_educational_plan_sections_delete_wil_requirement(request,pk,wil_pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        section = StudentEducationPlanSection.objects.get(id = pk)
        wil = StudentEducationPlanSectionWILRequirement.objects.get(id = wil_pk)
        
        try:
            wil.delete()
            messages.success(request,'Successfully removed wil requirement')
        except Exception as e:
            messages.warning(request,"An error has occurred")
           
        return redirect('students:view_learner_educational_plan_sections',pk=section.registration_id)
            
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
    
@login_required()
def view_learner_educational_plan(request,pk,registration_pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10):

        lp = StudentLearningProgramme.objects.get(id = pk)
        learning_programme = lp.learning_programme
        learning_programme_cohort = lp.learning_programme_cohort
        registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        registration_period = registration.registration_period
        weeks = EducationPlanYearSectionWeeks.objects.filter(education_plan_year_section__education_plan_year__cohort_registration_period = registration_period)
        
        health_facilities = HealthCareFacility.objects.all()
        hospitals = HealthCareFacility.objects.filter(category = 'Hospital')
        phcs = HealthCareFacility.objects.filter(category = 'Primary Health Care')
        blocks = ProgarmmeBlock.objects.all()
        disciplines = Discipline.objects.all()
        #check if plan has been copied over, if not then copy it over
        
        if registration.education_plans.count() == 0:
            for week in weeks:
                StudentEducationPlan.objects.create(
                    registration = registration,
                    education_plan_section_week = week,
                    time_period = week.time_period,
                    block = week.block,
                    facility_type = week.facility_type                    
                )
                
            
        if request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1:
            return render(request,'students/learner_education_plan.html',{
                'registration':registration,
                'lp':lp,
                'health_facilities':health_facilities,
                'cohort_menu':'--active',
                'hospitals':hospitals,
                'phcs':phcs,
                'blocks':blocks,
                'disciplines':disciplines,
                'learning_programme_cohort':learning_programme_cohort,
                'learning_programme':learning_programme,
                'registration_period':registration_period,
            })
        elif request.user.logged_in_role_id == 10:
            return render(request,'students/learning_programme/student_learner_education_plan.html',{
                'registration':registration,
                'lp':lp,
                'health_facilities':health_facilities,
                'reg_active':'--active',
                'hospitals':hospitals,
                'phcs':phcs,
                'blocks':blocks,
                'disciplines':disciplines,
                'learning_programme_cohort':learning_programme_cohort,
                'learning_programme':learning_programme,
                'registration_period':registration_period,
            })
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def assign_learner_educational_plan_hospital(request,pk,registration_pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        lp = StudentLearningProgramme.objects.get(id = pk)
        registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        capacity_reached = False
        
        for plan in registration.education_plans.all():
            #check if facility still has capacity
            facility = HealthCareFacility.objects.get(id = request.POST['hospital'])
            balance = facility.check_numbers_balance(lp.learning_programme,registration)
            if balance > 0:
                if plan.facility_type == 'H':
                    plan.facility_id = request.POST['hospital']
                    plan.save()
            else:
                capacity_reached = True
                break
        
        if capacity_reached:
            messages.warning(request,'Sorry the selected health care facility has reached capacity')
        else:        
            messages.success(request,'Successfully assigned hospital')
                
        return redirect('students:view_learner_educational_plan',pk=pk,registration_pk=registration_pk)
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def assign_learner_educational_plan_phc(request,pk,registration_pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        lp = StudentLearningProgramme.objects.get(id = pk)
        registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        capacity_reached = False
        
        for plan in registration.education_plans.all():
            #check if facility still has capacity
            facility = HealthCareFacility.objects.get(id = request.POST['phc'])
            balance = facility.check_numbers_balance(lp.learning_programme,registration)
            if balance > 0:
                if plan.facility_type == 'PHC':
                    plan.facility_id = request.POST['phc']
                    plan.save()
            else:
                capacity_reached = True
                break
            
        if capacity_reached:
            messages.warning(request,'Sorry the selected health care facility has reached capacity')
        else:         
            messages.success(request,'Successfully assigned Primary Healthcare Facility')
                
        return redirect('students:view_learner_educational_plan',pk=pk,registration_pk=registration_pk)
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def edit_learner_educational_plan(request,pk,registration_pk,week_pk):
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        lp = StudentLearningProgramme.objects.get(id = pk)
        registration = StudentLearningProgrammeRegistration.objects.get(id = registration_pk)
        education_plan_week = StudentEducationPlan.objects.get(id = week_pk)
        
        if request.POST['facility_type'] != 0:
            education_plan_week.facility_type = request.POST['facility_type']
            education_plan_week.save()
        
        if request.POST['facility'] != "0":
            facility = HealthCareFacility.objects.get(id = request.POST['facility'])
            #check if there is capacity
            balance = facility.check_numbers_balance(lp.learning_programme,registration)
            if balance > 0:
                if education_plan_week.facility_type == 'H':
                    if facility.category == "Hospital":
                        education_plan_week.facility = facility
                    else:
                        messages.warning(request,f'Selected Facility type ({education_plan_week.facility_type}) is different from the selected facility category ({facility.category})')
                elif education_plan_week.facility_type == 'PHC':
                    if facility.category == "Primary Health Care":
                        education_plan_week.facility = facility
                    else:
                        messages.warning(request,f'Selected Facility type ({education_plan_week.facility_type}) is different from the selected facility category ({facility.category})')
                    
            else:
                messages.warning(request,'Facility has reached capacity, learner cannot be added')
    
                        
        if 'block' in request.POST:
             education_plan_week.block_id = request.POST['block']    
        
        if 'time_period' in request.POST:
             education_plan_week.time_period = request.POST['time_period'] 
             
        if request.POST['discipline'] != "0":
            education_plan_week.discipline_id = request.POST['discipline'] 
             
        education_plan_week.save()
        
        messages.success(request,"Successfully edited week's information")      
              
        return redirect('students:view_learner_educational_plan',pk=pk,registration_pk=registration_pk)
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def view_learners_days(request,pk):
    
    '''
    days of the week
    '''
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 10):

        plan = StudentEducationPlan.objects.get(id = pk) 
        registration = plan.registration
        registration_period = registration.registration_period
        learning_programme = registration.student_learning_programme.learning_programme
        learning_programme_cohort = registration.student_learning_programme.learning_programme_cohort
        #check if days exist , if not add them
        if plan.days.count() == 0:
            # Generate a list of days between start_date and end_date
            days_in_week = [(plan.education_plan_section_week.start_of_week + datetime.timedelta(days=i)) for i in range(7)]
            for day in days_in_week:
                StudentEducationPlanDay.objects.create(
                    education_plan_section_week = plan,
                    day = day,
                )
                
        discipline = plan.discipline
        
        wards = discipline.wards.all()
        
        if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
            return render(request,'students/learner_education_plan_days.html',{
                                                                  'wards':wards,
                                                                  'discipline':discipline,
                                                                  'plan':plan,
                                                                  'registration':registration,
                                                                  'registration_period':registration_period,
                                                                  'learning_programme':learning_programme,
                                                                  'learning_programme_cohort':learning_programme_cohort,
                                                                  'cohort_menu':'--active',})
        elif request.user.logged_in_role_id == 10:
            
            return render(request,'students/learning_programme/student_learner_education_plan_days.html',{'wards':wards,
                                                                  'discipline':discipline,
                                                                  'plan':plan,
                                                                  'registration':registration,
                                                                  'reg_active':'--active',})
            
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def view_learners_days_timetable(request,pk,week_pk):
    
    '''
    days of the week time table
    '''
    
    if request.user.logged_in_role_id == 10:
        
        week = EducationPlanYearSectionWeeks.objects.get(id = week_pk)
        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        
        
        return render(request,'students/learning_programme/education_plan_days.html',{                                                                
                                                                  'week':week,
                                                                  'registration':registration,
                                                                  'reg_active':'--active',})
            
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def edit_learners_days(request,pk):
    
    '''
    days of the week
    '''
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1):

        days = request.POST.getlist('days_selected[]')
        for day_pk in days:
            day = StudentEducationPlanDay.objects.get(id = day_pk) 
            if request.POST['ward'] == '0':
                day.ward = None
            else:
                day.ward_id = request.POST['ward']
            day.save()
                
        messages.success(request,'Successfully edited ward')
        
        return redirect('students:view_learners_days',pk=pk)
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def learner_learning_programmes(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)
        
        learnng_programme_cohorts = StudentLearningProgramme.objects.filter(student = student)      
        return render(request,'students/student_learning_programmes.html',{'student':student,
                                                                           'learnng_programme_cohorts':learnng_programme_cohorts,
                                                                           'reg_active':'--active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def learner_learning_programme_registrations(request,pk):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)
        student_learning_programme = StudentLearningProgramme.objects.get(id = pk)
        registrations = student_learning_programme.registrations.all()
           
        return render(request,'students/student_learning_programme_registrations.html',{'student':student,
                                                                           'registrations':registrations,
                                                                           'student_learning_programme':student_learning_programme,
                                                                           'reg_active':'--active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def learner_registered_modules(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)
        
        modules = StudentRegistrationModule.objects.filter(registration__student_learning_programme__student = student)      
        
        return render(request,'students/student_modules.html',{'student':student,
                                                               'modules':modules,
                                                               'module_active':'--active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def ajax_validate_id_number(request):
    '''
    Check if the learner exists in the db
    '''
    id_number_check = request.GET.get('id_number', None)
    try:
        learner_check = Student.objects.filter(id_number = id_number_check)
        
        if learner_check.exists():
            learner = learner_check.first()            
            data = {
                'valid':1,
                'first_name':learner.first_name,
                'last_name':learner.last_name,
                'email':learner.email,
            }
        else:
            data = {
                'valid':0,
                'message':'Student with supplied ID Number does not exist, please complete the information to proceed'
            }
    except Exception as e:
        data = {
            'valid':0,
            'message':'Student with supplied ID Number does not exist, please complete the information to proceed'
        }

    return JsonResponse(data)



def ajax_fetch_highschools(request):
    province_id = request.GET.get('province_id', None)
    try:
        province_check = Province.objects.filter(id = province_id)

        if province_check.exists():
            province = province_check.first()
            data = {
                'valid':1,
                'province_id':province.id,
            }
            info = []
            for x in province.school_codes.all():
                info.append({'id':x.id,'high_school':x.Official_Institution_Name})

            data['info'] = info
        else:
            data = {
                'valid':0,
                'message':'No High Schools'
            }
    except Exception as e:
        data = {
            'valid':2,
            'message':'str(e)'
        }

    return JsonResponse(data)