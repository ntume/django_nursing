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
from io import BytesIO
import os
import json
import datetime
from wsgiref.util import FileWrapper
from io import StringIO
from zipfile import ZipFile

from accounts.models import User
from announcements.models import Announcement, LearningProgrammeCohortAnnouncement, LearningProgrammeCohortRegisteredAnnouncement
from appointments.models import Appointment
from college.models import EducationPlanYearSectionWeekDay, HealthCareFacility, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod
from configurable.models import Country, Disability, Gender, NQFLevel, Nationality, Province, Race, ResidentialStatus, Suburb, TypeOfID, TypeOfLeave
from django_nursing.email_functions import send_email_general
from students.views import learner_address_details, learner_education_details, learner_next_of_kin_details, learner_programme_details
from .forms import LearnerAddressForm, LearnerAttachementAuxillaryCertificateForm, LearnerAttachementIDForm, LearnerAttachementIndemnityForm, LearnerAttachementMarriageForm, LearnerAttachementMatricForm, LearnerAttachementOtherQualificationForm, LearnerAttachementPracticingCertificateForm, LearnerAttachementSAQAForm, LearnerAttachementSancCertificateForm, LearnerAttachementSancLearnerRegistrationForm, LearnerAttachementStudyPermitForm, LearnerExtendedForm, LearnerNextKinForm, StudentBasicForm, StudentCreateForm,StudentProfileForm,StudentProfilePicForm, StudentRegistrationLeaveForm
from .models import Student,Language, StudentLearningProgramme, StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationAttachment, StudentNextofKin, StudentRegistrationLeave, StudentRegistrationModule

from za_id_number.za_id_number import SouthAfricanIdentityValidate,SouthAfricanIdentityNumber

today = datetime.date.today()


@login_required()
def student_dashboard(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)
        
        current_week_days = None

        announcements = Announcement.objects.filter(start_date__lte = today, end_date__gte = today)
        cohort_announcements = []
        cohort_registration_announcements = []

        appointments = Appointment.objects.filter(student = student)
        all_leave = StudentRegistrationLeave.objects.filter(registration__student_learning_programme__student = student)

        registration,timetable,month_plans = None,None,None
        registration_check = StudentLearningProgrammeRegistration.objects.filter(student_learning_programme__student = student,
                                                                           registration_period__start_date__lte = today,
                                                                           registration_period__end_date__gte = today)
        
        months_appointments = appointments.filter(appointment_date__startswith = f'{today.year}-{today.strftime("%m")}')
        months_leave = all_leave.filter(from_date__startswith = f'{today.year}-{today.strftime("%m")}')
        
        #get education plan
        if registration_check.exists():
            registration = registration_check.last()
            timetable = registration.education_plans.all()

            cohort_announcements = LearningProgrammeCohortAnnouncement.objects.filter(learning_programme_cohort = registration.student_learning_programme.learning_programme_cohort)
            cohort_registration_announcements = LearningProgrammeCohortRegisteredAnnouncement.objects.filter(learning_programme_cohort_registration = registration.registration_period)
            #get this months details 
            month_plans = registration.education_plans.filter(education_plan_section_week__start_of_week__startswith = f'{today.year}-{today.strftime("%m")}')
            
            current_week_days = (EducationPlanYearSectionWeekDay.
                            objects.
                            filter(education_plan_section_week__start_of_week__lte = today,
                                   education_plan_section_week__end_of_week__gte = today,
                                   education_plan_section_week__education_plan_year_section__education_plan_year__cohort_registration_period = registration.registration_period))
                       
       
        return render(request,'students/student_info/student_dashboard.html',{'student':student,
                                                                              'appointments':appointments,
                                                                              'all_leave':all_leave,
                                                                              'today':today,
                                                                              'dash_active':'--active',
                                                                              'registration':registration,
                                                                              'timetable':timetable,
                                                                              'month_plans':month_plans,
                                                                              'months_appointments':months_appointments,
                                                                              'months_leave':months_leave,
                                                                              'announcements':announcements,
                                                                              'cohort_announcements':cohort_announcements,
                                                                              'cohort_registration_announcements':cohort_registration_announcements,
                                                                              'current_week_days':current_week_days,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def student_profile(request,page):
    '''
    Students Profile function
    '''
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)

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
        
        learner_details_page,education_page,next_of_kin_page,address_page,profile_picture_page,password_page = False,False,False,False,False,False
        
        if page == 1:
            learner_details_page = True
        if page == 2:
            address_page = True
        if page == 3:
            education_page = True
        if page == 4:
            next_of_kin_page = True
        if page == 5:
            profile_picture_page = True
        if page == 6:
            password_page = True

        return render(request,'students/student_info/profile/profile_tpl.html',{'student':student,
                                                                            'race':race,
                                                                            'gender':gender,
                                                                            'nqf_levels':nqf_levels,
                                                                            'areas':areas,
                                                                            'languages':languages,            
                                                                            'countries':countries,
                                                                            'disabilities':disabilities,
                                                                            'provinces':provinces,
                                                                            'type_of_ids':type_of_ids,
                                                                            'nationalities':nationalities,
                                                                            'residentrial_statuses':residentrial_statuses,
                                                                            'learner_details_page':learner_details_page,
                                                                            'education_page':education_page,
                                                                            'next_of_kin_page':next_of_kin_page,                                                                       
                                                                            'address_page':address_page,
                                                                            'profile_picture_page':profile_picture_page,
                                                                            'password_page':password_page,
                                                                            'profile_active':'--active',
                                                                            'lp_edit':'disabled'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_profile_personal_details(request,pk):
    '''
    Edit learner information
    '''

    if (request.user.logged_in_role_id == 10):
        
        learner_instance = Student.objects.get(id = pk)

        success = learner_programme_details(request,learner_instance)

        
        return render(request,'messages.html')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def edit_profile_address_details(request,pk):
    '''
    Edit learner address information
    '''

    if (request.user.logged_in_role_id == 10):
        
        learner_instance = Student.objects.get(id = pk)

        learner_address_details(request,learner_instance)
        
        return render(request,'messages.html')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_profile_education_details(request,pk):
    '''
    Edit learner education information
    '''

    if (request.user.logged_in_role_id == 10):
        
        learner_instance = Student.objects.get(id = pk)

        learner_education_details(request,learner_instance)
    
        return render(request,'messages.html')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def edit_profile_picture(request,pk):
    '''
    Edit learner education information
    '''

    if (request.user.logged_in_role_id == 10):
        
        learner_instance = Student.objects.get(id = pk)
        
        profile_pic = request.FILES.get('file')
        learner_instance.profile_pic = profile_pic
        learner_instance.save()
        
        
        form  = StudentProfilePicForm(request.POST,request.FILES,instance=learner_instance)
        if form.is_valid():
            form.save()
            messages.success(request,'Successfully uploaded profile picture')
        else:
            messages.warning(request,form.errors)
    
        return redirect('students:student_profile',page=5)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def add_profile_next_of_kin_details(request,pk):
    '''
    Add Next of Kin
    '''

    if (request.user.logged_in_role_id == 10):
        
        learner_instance = Student.objects.get(id = pk)

        learner_next_of_kin_details(request,learner_instance,'Add',None)
    
        return redirect('students:student_profile',page=4)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
    
@login_required()
def edit_profile_next_of_kin_details(request,pk,next_of_kin_pk):
    '''
    Add Next of Kin
    '''

    if (request.user.logged_in_role_id == 10):
        
        learner_instance = Student.objects.get(id = pk)
        next_of_kin = StudentNextofKin.objects.get(id = next_of_kin_pk)

        learner_next_of_kin_details(request,learner_instance,'Edit',next_of_kin)
    
        return redirect('students:student_profile',page=4)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    

@login_required()
def delete_profile_next_of_kin_details(request,pk,next_of_kin_pk):
    '''
    Add Next of Kin
    '''

    if (request.user.logged_in_role_id == 10):
        
        learner_instance = Student.objects.get(id = pk)
        next_of_kin = StudentNextofKin.objects.get(id = next_of_kin_pk)
        
        if learner_instance.next_of_kin.count() > 1:
            next_of_kin.delete()
            messages.success(request,'Successfully deleted Next of Kin')
        else:
            messages.warning(request,"You need to have at least one Next of Kin contact details")
    
        return redirect('students:student_profile',page=4)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')