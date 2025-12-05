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
from io import BytesIO
import os
import json
import datetime
from wsgiref.util import FileWrapper
from io import StringIO
from zipfile import ZipFile

from accounts.models import User
from accounts.views import create_user_profile_external, password_gen
from college.models import HealthCareFacility, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod
from configurable.models import Country, Disability, Gender, Indemnity, NQFLevel, Nationality, Province, Race, ResidentialStatus, Suburb, TypeOfID
from django_nursing.email_functions import send_email_general
from students.forms import LearnerAddressForm, LearnerAttachementAuxillaryCertificateForm, LearnerAttachementIDForm, LearnerAttachementIndemnityForm, LearnerAttachementMarriageForm, LearnerAttachementMatricForm, LearnerAttachementOtherQualificationForm, LearnerAttachementPracticingCertificateForm, LearnerAttachementSAQAForm, LearnerAttachementSancCertificateForm, LearnerAttachementSancLearnerRegistrationForm, LearnerAttachementStudyPermitForm, LearnerExtendedForm, LearnerNextKinForm, StudentBasicForm, StudentCreateForm,StudentProfileForm,StudentProfilePicForm
from students.models import Student,Language, StudentLearningProgramme, StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationAttachment, StudentRegistrationModule,StudentNextofKin

from students.views import learner_address_details, learner_education_details, learner_next_of_kin_details, learner_programme_details
from za_id_number.za_id_number import SouthAfricanIdentityValidate,SouthAfricanIdentityNumber


# Create your views here.

def open_onboarding(request,pk,slug,page):
    '''
    Function to start  the onboarding process
    '''
    
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
    hospitals = HealthCareFacility.objects.filter(category='Hospital')
    phcs = HealthCareFacility.objects.filter(category='Primary Health Care')
    indeminity = Indemnity.objects.all()
    
    '''
    check progress
    '''

    learner_completed,learner_reason = lp.student.check_completed_info()
    
    learner_details_page,education_page,next_of_kin_page,summary_page,address_page = False,False,False,False,False
    next_page = None
    previous_page = None
    
    if page == 1:
        learner_details_page = True
        next_page = 2
    if page == 2:
        address_page = True
        next_page = 3
        previous_page = 1
    if page == 3:
        education_page = True
        next_page = 4
        previous_page = 2
    if page == 4:
        next_of_kin_page = True
        next_page = 5
        previous_page = 3
    if page == 5:
        summary_page = True
        next_page = 6
        previous_page = 4
    

    
    return render(request,'api/students/onboarding_tpl.html',{            
            'lp':lp,
            'race':race,
            'gender':gender,
            'nqf_levels':nqf_levels,
            'areas':areas,
            'learner_completed':learner_completed,
            'learner_reason':learner_reason,
            'languages':languages,            
            'countries':countries,
            'disabilities':disabilities,
            'provinces':provinces,
            'type_of_ids':type_of_ids,
            'nationalities':nationalities,
            'residentrial_statuses':residentrial_statuses,
            'learning_programme_cohort':learning_programme_cohort,
            'learning_programme':learning_programme,
            'page':'learner_details',
            'next_page':next_page,
            'previous_page':previous_page,
            'learner_details_page':learner_details_page,
            'education_page':education_page,
            'next_of_kin_page':next_of_kin_page,
            'summary_page':summary_page,
            'address_page':address_page,
            'hospitals':hospitals,
            'indeminity':indeminity,
            'phcs':phcs,
        })

def edit_learner_programme_details(request,pk):
    '''
    Edit learner information
    '''

    lp = StudentLearningProgramme.objects.get(id = pk)
    learner_instance = lp.student

    success = learner_programme_details(request,learner_instance)

    
    return redirect('api:open_onboarding',pk=pk,slug=lp.student.slug,page=2)

    
def edit_learner_address_details(request,pk):
    '''
    Edit learner address information
    '''
   
    lp = StudentLearningProgramme.objects.get(id = pk)
    learner_instance = lp.student

    learner_address_details(request,learner_instance)
    
    return redirect('api:open_onboarding',pk=pk,slug=lp.student.slug,page=3)

    
def edit_learner_education_details(request,pk):
    '''
    Edit learner education information
    '''
 
    lp = StudentLearningProgramme.objects.get(id = pk)
    learner = lp.student

    learner_education_details(request,learner)

    return redirect('api:open_onboarding',pk=pk,slug=lp.student.slug,page=4)
    

def edit_learner_next_of_kin_details(request,pk):
    '''
    Edit learner parent or guardian information
    '''

    lp = StudentLearningProgramme.objects.get(id = pk)
    learner_instance = lp.student

    learner_next_of_kin_details(request,learner_instance)

    return redirect('api:open_onboarding',pk=pk,slug=lp.student.slug,page=5)



def add_profile_next_of_kin_details(request,pk):
    '''
    Add Next of Kin
    '''
        
    lp = StudentLearningProgramme.objects.get(id = pk)
    
    learner_instance = lp.student

    learner_next_of_kin_details(request,learner_instance,'Add',None)

    return redirect('api:open_onboarding',pk=pk,slug=learner_instance.slug,page=4)
 
    
    
    
@login_required()
def edit_profile_next_of_kin_details(request,pk,next_of_kin_pk):
    '''
    edit Next of Kin
    '''

    lp = StudentLearningProgramme.objects.get(id = pk)
    
    learner_instance = lp.student
    
    next_of_kin = StudentNextofKin.objects.get(id = next_of_kin_pk)

    learner_next_of_kin_details(request,learner_instance,'Edit',next_of_kin)

    return redirect('api:open_onboarding',pk=pk,slug=learner_instance.slug,page=4)
    
    
    
def delete_profile_next_of_kin_details(request,pk,next_of_kin_pk):
    '''
    delete Next of Kin
    '''
        
    lp = StudentLearningProgramme.objects.get(id = pk)
    
    learner_instance = lp.student
    
    next_of_kin = StudentNextofKin.objects.get(id = next_of_kin_pk)
    
    if learner_instance.next_of_kin.count() > 1:
        next_of_kin.delete()
        messages.success(request,'Successfully deleted Next of Kin')
    else:
        messages.warning(request,"You need to have at least one Next of Kin contact details")

    return redirect('api:open_onboarding',pk=pk,slug=learner_instance.slug,page=4)
    


def submit_onboarding_details(request,pk):
    '''
    Create Learner Profile
    '''

    lp = StudentLearningProgramme.objects.get(id = pk)
    student = lp.student
    
    if request.POST['password'] == request.POST['password2']:

        success,message = create_user_profile_external(student,10,request.POST['password'])
        
        if success:
            student.on_boarded = 'Yes'
            student.save()
            messages.success(request,'Successfully completed the onboarding process')
            return redirect('accounts:login_user')
        
    else:
        messages.warning(request,'The two passwords do not match, please try again')

    return redirect('api:open_onboarding',pk=pk,slug=lp.student.slug,page=5)


def confirm_learner_pop(request,pk):
    '''
    Check the learner pop
    '''
    found = False
    check_learner_registration = StudentLearningProgrammeRegistration.objects.filter(slug = pk)
    if check_learner_registration.exists():
        learner_registration = check_learner_registration.first()       
              
        learner_name = f'{learner_registration.student_learning_programme.student.first_name} {learner_registration.student_learning_programme.student.last_name}'
        qualification_title = learner_registration.student_learning_programme.learning_programme.programme_name
        qualification_id = learner_registration.student_learning_programme.learning_programme.programme_code
        student_number = learner_registration.student_learning_programme.student.student_number
        modules = learner_registration.registered_modules.all()

        return render(request,"api/registration/proof_of_registration.html",
                {
                    'qualification_title':qualification_title,
                    'qualification_id':qualification_id,
                    'modules':modules,
                    'registration_date':learner_registration.registration_date,
                    'learner_name':learner_name,
                    'found':True,
                    'student_number':student_number,
                    })

        
    else:
        msg = "Sorry the supplied student number does not appear in our registration records"
        return render(request,"api/registration/proof_of_registration.html",{'found':False,'msg':msg})

