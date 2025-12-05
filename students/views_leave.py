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
from io import BytesIO
import os
import json
import datetime
from wsgiref.util import FileWrapper
from io import StringIO
from zipfile import ZipFile

from accounts.models import User
from appointments.models import Appointment
from college.models import HealthCareFacility, LearningProgramme, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod, LearningProgrammePeriod
from configurable.models import Country, Disability, Gender, NQFLevel, Nationality, Province, Race, ResidentialStatus, Suburb, TypeOfID, TypeOfLeave
from django_nursing.email_functions import send_email_general
from django_nursing.utility_functions import number_of_days
from students.views import learner_address_details, learner_education_details, learner_next_of_kin_details, learner_programme_details
from .forms import LearnerAddressForm, LearnerAttachementAuxillaryCertificateForm, LearnerAttachementIDForm, LearnerAttachementIndemnityForm, LearnerAttachementMarriageForm, LearnerAttachementMatricForm, LearnerAttachementOtherQualificationForm, LearnerAttachementPracticingCertificateForm, LearnerAttachementSAQAForm, LearnerAttachementSancCertificateForm, LearnerAttachementSancLearnerRegistrationForm, LearnerAttachementStudyPermitForm, LearnerExtendedForm, LearnerNextKinForm, StudentBasicForm, StudentCreateForm,StudentProfileForm,StudentProfilePicForm, StudentRegistrationLeaveFileForm, StudentRegistrationLeaveForm
from .models import Student,Language, StudentLearningProgramme, StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationAttachment, StudentNextofKin, StudentRegistrationLeave, StudentRegistrationModule

from za_id_number.za_id_number import SouthAfricanIdentityValidate,SouthAfricanIdentityNumber

today = datetime.date.today()

@login_required()
def student_leave(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)

        #check_registration

        registration_check = StudentLearningProgrammeRegistration.objects.filter(student_learning_programme__student = student)

        if registration_check.exists():
            registration = registration_check.first()
            all_leave = registration.leave_requests.all()

            leave_types = TypeOfLeave.objects.all()    

            leave_type_breakdown = []

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


        
            return render(request,'students/student_leave/student_leave.html',{'student':student,
                                                                 'all_leave':all_leave,
                                                                 'registration':registration,
                                                                 'leave_types':leave_types,
                                                                 'today':today,
                                                                 'leave_active':'--active',
                                                                 'leave_type_breakdown':leave_type_breakdown})
        
        else:
            messages.warning(request,'Sorry you are not registered')
            return redirect('students:student_dashboard')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def student_leave_request_submission(request,pk):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)

        #check_registration

        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        
        #check if leave requested in the same period
        
        check_leave = (StudentRegistrationLeave.
                       objects.
                       filter(
                           Q(registration = registration) & 
                           (Q(from_date__lte=request.POST['to_date'], to_date__gte=request.POST['from_date']))).
                       exclude(status='Rejected'))
        
        if check_leave.exists():
            messages.warning(request,"You have a leave request pending in the same period.")
        else:

            form = StudentRegistrationLeaveForm(request.POST)
            if form.is_valid():
                leave = form.save(commit = False)
                leave.registration = registration
                leave.type_of_leave_id = request.POST['type_of_leave']
                leave.number_of_days = number_of_days(leave.from_date,leave.to_date)
                leave.save()
                
                if 'file' in request.FILES:
                    file_form = StudentRegistrationLeaveFileForm(request.POST,request.FILES,instance=leave)
                    if file_form.is_valid():
                        file_form.save()
                        messages.success(request,'Successfully uploaded file')
                    else:
                        messages.warning(request,file_form.errors)

                messages.success(request,'Successfully added your request, please wait for approval')
            else:
                messages.warning(request,form.errors)

        return redirect('students:student_leave')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def student_leave_request_submission_edit(request,pk,leave_pk):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user = request.user)
        leave = StudentRegistrationLeave.objects.get(id = leave_pk)

        #check_registration

        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        
        check_leave = (StudentRegistrationLeave.
                       objects.
                       filter(
                           Q(registration = registration) & 
                           (Q(from_date__lte=request.POST['to_date'], to_date__gte=request.POST['from_date']))).
                       exclude(status='Rejected',id=leave.id))
        
        if check_leave.exists():
            messages.warning(request,"You have a leave request pending in the same period.")
        else:
            form = StudentRegistrationLeaveForm(request.POST,instance=leave)
            if form.is_valid():
                leave = form.save(commit = False)
                leave.registration = registration
                leave.type_of_leave_id = request.POST['type_of_leave']
                leave.number_of_days = number_of_days(leave.from_date,leave.to_date)
                leave.save()
                
                if 'file' in request.FILES:
                    file_form = StudentRegistrationLeaveFileForm(request.POST,request.FILES,instance=leave)
                    if file_form.is_valid():
                        file_form.save()
                        messages.success(request,'Successfully uploaded file')
                    else:
                        messages.warning(request,file_form.errors)

                messages.success(request,'Successfully edited your request, please wait for approval')
            else:
                messages.warning(request,form.errors)

        return redirect('students:student_leave')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

'''
Lecturer Approval
'''


class RequestedLeaveReportList(LoginRequiredMixin,ListView):
    template_name = 'students/student_leave/requested_leave_report.html'
    context_object_name = 'learners'
    paginate_by = 10

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(RequestedLeaveReportList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  StudentRegistrationLeave.objects.filter(approved = 'Pending',registration__registration_period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = registration_period.learning_programme_cohort.learning_programme
        context['learning_programme_cohort'] = registration_period.learning_programme_cohort
        context['learning_programme_cohort_registration'] = registration_period
        context['leave_menu'] = '--active'
        context['type_of_leave'] = TypeOfLeave.objects.all()
        return context
    
    
    
@login_required()
def requested_leave_list_filter(request,pk):
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        leave_requests = StudentRegistrationLeave.objects.filter(registration__registration_period_id = pk)
        if request.method == "POST":
            page = 1
            
            if request.POST['type_of_leave'] != "0":
                leave_requests = leave_requests.filter(type_of_leave_id = request.POST['type_of_leave'])
            if request.POST['approved'] != "0":
                leave_requests = leave_requests.filter(approved = request.POST['approved'])
            
            filter = [request.POST['type_of_leave'],request.POST['approved'],]
            filterstr = '*'.join(filter)

            paginator = Paginator(leave_requests, 10)

            try:
                learners = paginator.page(page)
            except PageNotAnInteger:
                learners = paginator.page(1)
            except EmptyPage:
                learners = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('*')

                if filter[0] != "":
                    leave_requests = leave_requests.filter(type_of_leave_id = filter[0])
                if filter[1] != "":
                    leave_requests = leave_requests.filter(approved = filter[1])
            
            paginator = Paginator(leave_requests, 10)
            try:
                learners = paginator.page(page)
            except PageNotAnInteger:
                learners = paginator.page(1)
            except EmptyPage:
                learners = paginator.page(paginator.num_pages)
                
        type_of_leave = TypeOfLeave.objects.all()

        registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        learning_programme = registration_period.learning_programme_cohort.learning_programme
        learning_programme_cohort = registration_period.learning_programme_cohort

        return render(request,
                      'students/student_leave/requested_leave_report.html',
                      {'learners':learners,
                       'filter':filterstr,
                       'type_of_leave':type_of_leave,
                       'registration_period':registration_period,
                       'learning_programme':learning_programme,
                       'learning_programme_cohort':learning_programme_cohort,
                       'leave_menu':'--active', 
                       })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class LeaveLearningProgrammeCohortList(LoginRequiredMixin,ListView):
    template_name = 'students/student_leave/learning_programme_cohorts.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LeaveLearningProgrammeCohortList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCohort.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['periods'] = LearningProgrammePeriod.objects.filter(learning_programme_id = self.kwargs['pk'])
        context['leave_menu'] = '--active'
        return context



class LeaveLearningProgrammeCohortRegistrationPeriodList(LoginRequiredMixin,ListView):
    template_name = 'students/student_leave/learning_programme_cohort_registrations.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LeaveLearningProgrammeCohortRegistrationPeriodList, self).get(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.logged_in_role_id == 1:
            return  LearningProgrammeCohortRegistrationPeriod.objects.filter(learning_programme_cohort_id = self.kwargs['pk'])
        else:
            return  LearningProgrammeCohortRegistrationPeriod.objects.filter(learning_programme_cohort_id = self.kwargs['pk'],
                                                                             programme_coordinator=self.request.user)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = self.kwargs['pk'])
        context['learning_programme_cohort'] = learning_programme_cohort 
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['periods'] = LearningProgrammePeriod.objects.filter(learning_programme_id = learning_programme_cohort.learning_programme_id)
        context['leave_menu'] = '--active'
        return context
    


class RequestedLeaveList(LoginRequiredMixin,ListView):
    template_name = 'students/student_leave/requested_leave.html'
    context_object_name = 'learners'
    paginate_by = 10

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(RequestedLeaveList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  StudentRegistrationLeave.objects.filter(approved = 'Pending',registration__registration_period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = registration_period.learning_programme_cohort.learning_programme
        context['learning_programme_cohort'] = registration_period.learning_programme_cohort
        context['learning_programme_cohort_registration'] = registration_period
        context['leave_menu'] = '--active'
        context['leave_types'] = TypeOfLeave.objects.all() 
        context['type_of_leave'] = TypeOfLeave.objects.all()
        return context


@login_required()
def requested_leave_cohorts_registrations_leave_filter(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
      
        leave_requests = StudentRegistrationLeave.objects.filter(registration__registration_period_id = pk)
        if request.method == "POST":
            page = 1
            
            if request.POST['type_of_leave'] != "0":
                leave_requests = leave_requests.filter(type_of_leave_id = request.POST['type_of_leave'])
            if request.POST['approved'] != "0":
                leave_requests = leave_requests.filter(approved = request.POST['approved'])
            
            filter = [request.POST['type_of_leave'],request.POST['approved'],]
            filterstr = '*'.join(filter)

            paginator = Paginator(leave_requests, 10)

            try:
                learners = paginator.page(page)
            except PageNotAnInteger:
                learners = paginator.page(1)
            except EmptyPage:
                learners = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('*')

                if filter[0] != "":
                    leave_requests = leave_requests.filter(type_of_leave_id = filter[0])
                if filter[1] != "":
                    leave_requests = leave_requests.filter(approved = filter[1])
            
            paginator = Paginator(leave_requests, 10)
            try:
                learners = paginator.page(page)
            except PageNotAnInteger:
                learners = paginator.page(1)
            except EmptyPage:
                learners = paginator.page(paginator.num_pages)
                
        type_of_leave = TypeOfLeave.objects.all()

        registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        learning_programme = registration_period.learning_programme_cohort.learning_programme
        learning_programme_cohort = registration_period.learning_programme_cohort
        leave_types = TypeOfLeave.objects.all() 
        
        return render(request,
                      'students/student_leave/requested_leave.html',
                      {'learners':learners,
                       'filter':filterstr,
                       'type_of_leave':type_of_leave,
                       'registration_period':registration_period,
                       'learning_programme':learning_programme,
                       'learning_programme_cohort':learning_programme_cohort,
                       'leave_menu':'--active', 
                       'learning_programme_cohort_registration':registration_period,
                       'leave_types':leave_types,
                       })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def requested_leave_edit(request,pk,leave_pk):
    
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        leave = StudentRegistrationLeave.objects.get(id = leave_pk)

        leave.approved = request.POST['approved']
        
        if 'type_of_leave' in request.POST:
            leave.type_of_leave_id = request.POST['type_of_leave']
        
        if 'approval_comment' in request.POST:
            leave.approval_comment = request.POST['approval_comment']
            
        leave.save()
            
        messages.success(request,f"Successfully {request.POST['approved']} leave request")
          
        return redirect('students:requested_leave_cohorts_registrations_leave',pk=pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')