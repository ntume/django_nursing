import decimal
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
from datetime import datetime, timedelta, date
from io import BytesIO
import os
import json

from wsgiref.util import FileWrapper
from io import StringIO
from zipfile import ZipFile

from accounts.models import User
from appointments.models import Appointment
from college.models import CohortRegistrationPeriodModule, CohortRegistrationPeriodModuleFormative, CohortRegistrationPeriodModuleRegister, CohortRegistrationPeriodModuleRegisterStudents, CohortRegistrationProcedure, CohortRegistrationProcedureSummative, CohortRegistrationProcedureSummativeTaskAssessment, CohortRegistrationProcedureTaskAssessment, EducationPlanYearSection, HealthCareFacility, HealthCareFacilityHOD, HealthCareFacilityWard, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod, LearningProgrammeModule, LearningProgrammeModuleStudyUnit
from configurable.models import ClinicalProcedureThemeTask, Country, Disability, Discipline, Gender, NQFLevel, Nationality, ProgarmmeBlock, Province, Race, ResidentialStatus, ShiftType, Suburb, TypeOfID, TypeOfLeave, Ward
from django_nursing.email_functions import send_email_general
from students.views import learner_address_details, learner_education_details, learner_next_of_kin_details, learner_programme_details
from .forms import LearnerAddressForm, LearnerAttachementAuxillaryCertificateForm, LearnerAttachementIDForm, LearnerAttachementIndemnityForm, LearnerAttachementMarriageForm, LearnerAttachementMatricForm, LearnerAttachementOtherQualificationForm, LearnerAttachementPracticingCertificateForm, LearnerAttachementSAQAForm, LearnerAttachementSancCertificateForm, LearnerAttachementSancLearnerRegistrationForm, LearnerAttachementStudyPermitForm, LearnerExtendedForm, LearnerNextKinForm, SIMProcedureLogForm, StudentBasicForm, StudentCreateForm, StudentLogSheetForm,StudentProfileForm,StudentProfilePicForm, StudentRegistrationLeaveForm
from .models import SIMProcedureLog, Student,Language, StudentEducationPlan, StudentEducationPlanDay, StudentEducationPlanSectionWILRequirement, StudentLearningProgramme, StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationAttachment, StudentLogSheet, StudentLogSheetAssessment, StudentNextofKin, StudentProcedureFormative, StudentProcedureFormativeAssessment, StudentProcedureFormativeAssessmentAnswer, StudentProcedureFormativeAssessmentAttempt, StudentProcedureSummative, StudentProcedureSummativeAssessment, StudentProcedureSummativeAssessmentAnswer, StudentProcedureSummativeAssessmentAttempt, StudentRegistrationLeave, StudentRegistrationModule, StudentRegistrationModuleAssessments

from za_id_number.za_id_number import SouthAfricanIdentityValidate,SouthAfricanIdentityNumber

today = date.today()

def time_difference(date1,time1,date2,time2):
    '''
    Calculate hours between two times
    '''
    

    # Combine date and time into datetime objects
    datetime1 = datetime.combine(date1, time1)
    datetime2 = datetime.combine(date2, time2)

    # Calculate the difference
    time_difference = datetime2 - datetime1

    # Convert the difference to hours
    difference_in_hours = time_difference.total_seconds() / 3600
    
    return difference_in_hours

class StudentLearningProgrammeList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/learning_programmes.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  StudentLearningProgramme.objects.filter(student__user = self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reg_active'] = '--active'
        return context
    
    
class StudentLearningProgrammeRegistrationList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/student_learning_programme_registrations.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationList, self).get(*args, **kwargs)

    def get_queryset(self):
        learning_programme_cohort = StudentLearningProgramme.objects.get(id = self.kwargs['pk'])
        return  learning_programme_cohort.registrations.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_learning_programme = StudentLearningProgramme.objects.get(id = self.kwargs['pk'])
        context['student_learning_programme'] = student_learning_programme
        context['learning_programme'] = student_learning_programme.learning_programme
        context['reg_active'] = '--active'
        return context
    


@login_required()
def student_view_logsheet(request,pk):
    '''
    Logsheet
    '''

    if (request.user.logged_in_role_id == 10 or 
        request.user.logged_in_role_id == 1 or 
        request.user.logged_in_role_id == 6 or 
        request.user.logged_in_role_id == 4):
        
        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        simulated_blocks = ProgarmmeBlock.objects.filter(internal = 'Yes',wil='Yes')
        non_simulated_blocks = ProgarmmeBlock.objects.filter(internal = 'No',wil='Yes')
        
        if request.user.logged_in_role_id == 10:
            template = 'students/learning_programme/wil/logsheet_tpl.html'
        else:
            template = 'students/learning_programme/wil_staff/logsheet_tpl.html'
            
        return render(request,template,
                      {'registration':registration,
                       'period':period,
                       'student':student,
                       'simulated_blocks':simulated_blocks,
                       'non_simulated_blocks':non_simulated_blocks,
                       'reg_active':'--active'})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    

class StudentLearningProgrammeRegistrationSimulatedWILLogsheetList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/wil/logsheet_tpl.html'
    context_object_name = 'entries'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationSimulatedWILLogsheetList, self).get(*args, **kwargs)

    def get_queryset(self):
        return StudentLogSheet.objects.filter(registration_id = self.kwargs['pk'],
                                              block_id = self.kwargs['block_pk'],
                                              date__month = self.kwargs['month_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        blocks = ProgarmmeBlock.objects.all()
        context['today'] = today
        context['selected_month'] = self.kwargs['month_pk']
        context['months'] = [
                    {'month':'Jan','id':'1'},
                    {'month':'Feb','id':'2'},
                    {'month':'Mar','id':'3'},
                    {'month':'Apr','id':'4'},
                    {'month':'May','id':'5'},
                    {'month':'June','id':'6'},
                    {'month':'Jul','id':'7'},
                    {'month':'Aug','id':'8'},
                    {'month':'Sept','id':'9'},
                    {'month':'Oct','id':'10'},
                    {'month':'Nov','id':'11'},
                    {'month':'Dec','id':'12'},
                ]
        context['time_choices'] = [                                    
                                    '07:00',
                                    '08:00',
                                    '09:00',
                                    '10:00',
                                    '11:00',
                                    '12:00',
                                    '13:00',
                                    '14:00',
                                    '15:00',
                                    '16:00',
                                    '17:00',
                                    '18:00',                                    
                                ]
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['blocks'] = blocks
        context['procedures'] = registration.registration_period.cohort_period_procedures.all()
        context['shifts'] = ShiftType.objects.all()
        context['programme_block'] = ProgarmmeBlock.objects.get(id = self.kwargs['block_pk'])     
        context['reg_active'] = '--active'
        context['simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'Yes',wil='Yes')
        context['non_simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'No',wil='Yes')
        context['simulated'] = True
        return context
    
    
class StudentLearningProgrammeRegistrationNonSimulatedWILLogsheetList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/wil/logsheet_tpl.html'
    context_object_name = 'entries'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationNonSimulatedWILLogsheetList, self).get(*args, **kwargs)

    def get_queryset(self):
        return StudentLogSheet.objects.filter(registration_id = self.kwargs['pk'],
                                              block_id = self.kwargs['block_pk'],
                                              date__month = self.kwargs['month_pk']).order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        blocks = ProgarmmeBlock.objects.all()
        context['today'] = today
        context['selected_month'] = self.kwargs['month_pk']
        context['months'] = [
                    {'month':'Jan','id':'1'},
                    {'month':'Feb','id':'2'},
                    {'month':'Mar','id':'3'},
                    {'month':'Apr','id':'4'},
                    {'month':'May','id':'5'},
                    {'month':'June','id':'6'},
                    {'month':'Jul','id':'7'},
                    {'month':'Aug','id':'8'},
                    {'month':'Sept','id':'9'},
                    {'month':'Oct','id':'10'},
                    {'month':'Nov','id':'11'},
                    {'month':'Dec','id':'12'},
                ]
        context['time_choices_old'] = [
                                ('00:00', '00:00 AM'),
                                ('01:00', '01:00 AM'),
                                ('02:00', '02:00 AM'),
                                ('03:00', '03:00 AM'),
                                ('04:00', '04:00 AM'),
                                ('05:00', '05:00 AM'),
                                ('06:00', '06:00 AM'),
                                ('07:00', '07:00 AM'),
                                ('08:00', '08:00 AM'),
                                ('09:00', '09:00 AM'),
                                ('10:00', '10:00 AM'),
                                ('11:00', '11:00 AM'),
                                ('12:00', '12:00 PM'),
                                ('13:00', '01:00 PM'),
                                ('14:00', '02:00 PM'),
                                ('15:00', '03:00 PM'),
                                ('16:00', '04:00 PM'),
                                ('17:00', '05:00 PM'),
                                ('18:00', '06:00 PM'),
                                ('19:00', '07:00 PM'),
                                ('20:00', '08:00 PM'),
                                ('21:00', '09:00 PM'),
                                ('22:00', '10:00 PM'),
                                ('23:00', '11:00 PM'),
                            ]
        context['time_choices'] = [f"{i:02}" for i in range(24)]
        context['time_minutes'] = [f"{i:02}" for i in range(60)]
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['blocks'] = blocks
        context['disciplines'] = Discipline.objects.all()
        context['shifts'] = ShiftType.objects.all()
        context['wards'] = Ward.objects.all()
        context['programme_block'] = ProgarmmeBlock.objects.get(id = self.kwargs['block_pk'])     
        context['reg_active'] = '--active'
        context['simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'Yes',wil='Yes')
        context['non_simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'No',wil='Yes')
        context['simulated'] = False
        return context
    


class StudentLearningProgrammeRegistrationSimulatedWILLogsheetStaffList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/wil_staff/logsheet_tpl.html'
    context_object_name = 'entries'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6 and self.request.user.logged_in_role_id != 10 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationSimulatedWILLogsheetStaffList, self).get(*args, **kwargs)

    def get_queryset(self):
        return StudentLogSheet.objects.filter(registration_id = self.kwargs['pk'],
                                              block_id = self.kwargs['block_pk'],
                                              date__month = self.kwargs['month_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        blocks = ProgarmmeBlock.objects.all()
        context['today'] = today
        context['selected_month'] = self.kwargs['month_pk']
        context['months'] = [
                    {'month':'Jan','id':'1'},
                    {'month':'Feb','id':'2'},
                    {'month':'Mar','id':'3'},
                    {'month':'Apr','id':'4'},
                    {'month':'May','id':'5'},
                    {'month':'June','id':'6'},
                    {'month':'Jul','id':'7'},
                    {'month':'Aug','id':'8'},
                    {'month':'Sept','id':'9'},
                    {'month':'Oct','id':'10'},
                    {'month':'Nov','id':'11'},
                    {'month':'Dec','id':'12'},
                ]
        context['time_choices'] = [                                    
                                    '07:00',
                                    '08:00',
                                    '09:00',
                                    '10:00',
                                    '11:00',
                                    '12:00',
                                    '13:00',
                                    '14:00',
                                    '15:00',
                                    '16:00',
                                    '17:00',
                                    '18:00',                                    
                                ]
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['blocks'] = blocks
        context['procedures'] = registration.registration_period.cohort_period_procedures.all()
        context['shifts'] = ShiftType.objects.all()
        context['programme_block'] = ProgarmmeBlock.objects.get(id = self.kwargs['block_pk'])     
        context['reg_active'] = '--active'
        context['simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'Yes',wil='Yes')
        context['non_simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'No',wil='Yes')
        context['simulated'] = True
        return context
    

class StudentLearningProgrammeRegistrationNonSimulatedWILLogsheetStaffList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/wil_staff/logsheet_tpl.html'
    context_object_name = 'entries'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6 and self.request.user.logged_in_role_id != 10 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationNonSimulatedWILLogsheetStaffList, self).get(*args, **kwargs)

    def get_queryset(self):
        return StudentLogSheet.objects.filter(registration_id = self.kwargs['pk'],
                                              block_id = self.kwargs['block_pk'],
                                              date__month = self.kwargs['month_pk']).order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        blocks = ProgarmmeBlock.objects.all()
        context['today'] = today
        context['selected_month'] = self.kwargs['month_pk']
        context['months'] = [
                    {'month':'Jan','id':'1'},
                    {'month':'Feb','id':'2'},
                    {'month':'Mar','id':'3'},
                    {'month':'Apr','id':'4'},
                    {'month':'May','id':'5'},
                    {'month':'June','id':'6'},
                    {'month':'Jul','id':'7'},
                    {'month':'Aug','id':'8'},
                    {'month':'Sept','id':'9'},
                    {'month':'Oct','id':'10'},
                    {'month':'Nov','id':'11'},
                    {'month':'Dec','id':'12'},
                ]
        context['time_choices_old'] = [
                                ('00:00', '00:00 AM'),
                                ('01:00', '01:00 AM'),
                                ('02:00', '02:00 AM'),
                                ('03:00', '03:00 AM'),
                                ('04:00', '04:00 AM'),
                                ('05:00', '05:00 AM'),
                                ('06:00', '06:00 AM'),
                                ('07:00', '07:00 AM'),
                                ('08:00', '08:00 AM'),
                                ('09:00', '09:00 AM'),
                                ('10:00', '10:00 AM'),
                                ('11:00', '11:00 AM'),
                                ('12:00', '12:00 PM'),
                                ('13:00', '01:00 PM'),
                                ('14:00', '02:00 PM'),
                                ('15:00', '03:00 PM'),
                                ('16:00', '04:00 PM'),
                                ('17:00', '05:00 PM'),
                                ('18:00', '06:00 PM'),
                                ('19:00', '07:00 PM'),
                                ('20:00', '08:00 PM'),
                                ('21:00', '09:00 PM'),
                                ('22:00', '10:00 PM'),
                                ('23:00', '11:00 PM'),
                            ]
        context['time_choices'] = [f"{i:02}" for i in range(24)]
        context['time_minutes'] = [f"{i:02}" for i in range(60)]
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['blocks'] = blocks
        context['disciplines'] = Discipline.objects.all()
        context['shifts'] = ShiftType.objects.all()
        context['wards'] = Ward.objects.all()
        context['programme_block'] = ProgarmmeBlock.objects.get(id = self.kwargs['block_pk'])     
        context['reg_active'] = '--active'
        context['simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'Yes',wil='Yes')
        context['non_simulated_blocks'] = ProgarmmeBlock.objects.filter(internal = 'No',wil='Yes')
        context['simulated'] = False
        return context
    

@login_required()
def add_logsheet(request,pk,block_pk,month_pk):
    '''
    Add Logsheet
    '''

    if (request.user.logged_in_role_id == 10):
        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        block = ProgarmmeBlock.objects.get(id = block_pk)
        
        form = StudentLogSheetForm(request.POST)
        
        if form.is_valid():
            logsheet = form.save(commit = False)

            if 'shift' in request.POST:
                logsheet.shift_id = request.POST['shift']
                
            if 'cohort_procedure' in request.POST:
                logsheet.cohort_procedure_id = request.POST['cohort_procedure']
                
            if 'discipline' in request.POST:
                logsheet.discipline_id = request.POST['discipline']
                                
            if 'facility_ward' in request.POST:
                #logsheet.ward_id = request.POST['facility_ward']
                logsheet.facility_ward_id = request.POST['facility_ward']
                
            logsheet.registration = registration                
            logsheet.block = block
            logsheet.start = datetime.strptime(f"{request.POST['start_hour']}:{request.POST['start_minutes']}:00", "%H:%M:%S").time()
            logsheet.end = datetime.strptime(f"{request.POST['end_hour']}:{request.POST['end_minutes']}:00", "%H:%M:%S").time()
            
            hours = time_difference(logsheet.date,logsheet.start,logsheet.end_date,logsheet.end)
            
            if hours < 0.0:
                messages.warning(request,'Sorry the time cannot be in negatives, please check your dates and time inputs')
            else:
                logsheet.hours = hours
                logsheet.save()                             
                messages.success(request,'Successfully added log entry')
                
        else:
            messages.warning(request,form.errors)
                
        if block.internal == 'Yes':
            return redirect('students:simulated_wil_logsheets',pk = registration.id,block_pk=block_pk,month_pk=month_pk)
        else:
            return redirect('students:non_simulated_wil_logsheets',pk = registration.id,block_pk=block_pk,month_pk=month_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
    
@login_required()
def edit_logsheet(request,pk,block_pk,month_pk,entry_pk):
    '''
    Add Logsheet
    '''

    if (request.user.logged_in_role_id == 10):
        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        block = ProgarmmeBlock.objects.get(id = block_pk)
        entry = StudentLogSheet.objects.get(id = entry_pk)
        
        form = StudentLogSheetForm(request.POST,instance=entry)
        
        if form.is_valid():
            logsheet = form.save(commit = False)
            if 'shift' in request.POST:
                logsheet.shift_id = request.POST['shift']
                
            if 'cohort_procedure' in request.POST:
                logsheet.cohort_procedure_id = request.POST['cohort_procedure']
                
            if 'discipline' in request.POST:
                logsheet.discipline_id = request.POST['discipline']
                                
            if 'facility_ward' in request.POST:
                logsheet.facility_ward_id = request.POST['facility_ward']
                
            hours = time_difference(logsheet.date,logsheet.start,logsheet.end_date,logsheet.end)
            
            
            if hours < 0.0:
                messages.warning(request,'Sorry the time cannot be in negatives, please check your dates and time inputs')
            else:
                logsheet.hours = hours
                logsheet.save()                             
                messages.success(request,'Successfully edited log entry')
        else:
            messages.warning(request,form.errors)
                
        
        if block.internal == 'Yes':
            return redirect('students:simulated_wil_logsheets',pk = registration.id,block_pk=block_pk,month_pk=month_pk)
        else:
            return redirect('students:non_simulated_wil_logsheets',pk = registration.id,block_pk=block_pk,month_pk=month_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def delete_logsheet(request,pk,block_pk,month_pk,entry_pk):
    '''
    Delete Logsheet
    '''

    if (request.user.logged_in_role_id == 10):
        
        entry = StudentLogSheet.objects.get(id = entry_pk)
        block = ProgarmmeBlock.objects.get(id = block_pk)
        
        try:
            entry.delete()
            messages.success(request,'Successfully deleted entry')
        except Exception as e:
            messages.warning(request,str(e))
    
        if block.internal == 'Yes':
            return redirect('students:simulated_wil_logsheets',pk = pk,block_pk=block_pk,month_pk=month_pk)
        else:
            return redirect('students:non_simulated_wil_logsheets',pk = pk,block_pk=block_pk,month_pk=month_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def wil_logsheet_hours(request,pk):
    '''
    WIL Logsheet
    '''

    if (request.user.logged_in_role_id == 10 or 
        request.user.logged_in_role_id == 1 or
        request.user.logged_in_role_id == 6 or 
        request.user.logged_in_role_id == 4):
        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        wil_hours = StudentEducationPlanSectionWILRequirement.objects.filter(student_education_plan_section__registration = registration)
        disciplines = Discipline.objects.all()
        logsheets = registration.logsheets.all()
        wards = Ward.objects.all()

        plan_year_section = None

        #find out what section we are in
        plan_year_section_check = EducationPlanYearSection.objects.filter(start_date__lte = today, 
                                                                    end_date__gte = today,
                                                                    education_plan_year__cohort_registration_period = registration.registration_period)
        if plan_year_section_check.exists():
            plan_year_section = plan_year_section_check.first()
            print(plan_year_section.section)

        discipline_hours = []
        ward_hours = []

        #check the discipline hours captured and summarize the information
        for d in disciplines:
            discipline_map = {'discipline':d}        
            #check if there are any hours captured
            discipline_map['hours'] = logsheets.filter(discipline = d).aggregate(Sum('hours'))['hours__sum'] or 0
            if plan_year_section:
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

        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        blocks = ProgarmmeBlock.objects.all()
        shifts = ShiftType.objects.all()
        simulated_blocks = ProgarmmeBlock.objects.filter(internal = 'Yes',wil='Yes')
        non_simulated_blocks = ProgarmmeBlock.objects.filter(internal = 'No',wil='Yes')
        simulated = False

        if (request.user.logged_in_role_id == 10):
            template = 'students/learning_programme/wil/logsheet_tpl.html'

        if (request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 4):
            template = 'students/learning_programme/wil_staff/logsheet_tpl.html'

        return render(request,
                      template,
                      {'ward_hours':ward_hours,
                       'discipline_hours':discipline_hours,
                       'registration':registration,
                       'period':period,
                       'student':student,
                       'blocks':blocks,
                       'disciplines':disciplines,
                       'reg_active':'--active',
                       'shifts':shifts,
                       'summary':True,
                       'non_simulated_blocks':non_simulated_blocks,
                       'simulated_blocks':simulated_blocks,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class StudentLearningProgrammeRegistrationModuleList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/registered_modules.html'
    context_object_name = 'modules'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationModuleList, self).get(*args, **kwargs)

    def get_queryset(self):
        module_list = []
        registered_modules = StudentRegistrationModule.objects.filter(registration_id = self.kwargs['pk'])

        for module in registered_modules:
            #check if an assessment has been added for the student
            module_map = {'module':module}
            assessment_list = []
            assignment = 0
            count_assignments = 0
            test = 0
            count_tests = 0
            assignment_avg = 0
            test_avg = 0
            assignment_percentage,test_percentage = 0,0
            for assessment in module.module.formative.all():
                if assessment.assessment_type == 'Assignment':
                    count_assignments = count_assignments + 1
                else:
                    count_tests = count_tests + 1

                assessment_map = {'assessment':assessment}
                check_assessment = StudentRegistrationModuleAssessments.objects.filter(student_registration_module=module,
                                                                                   assessment = assessment)
                if check_assessment.exists():
                    fetched_assessment = check_assessment.first()
                    assessment_map['marks'] = fetched_assessment.marks
                    if fetched_assessment.marks != None:
                        if assessment.assessment_type == 'Assignment':
                            assignment = assignment + fetched_assessment.marks                            
                        else:
                            test = test + fetched_assessment.marks                            
                else:
                    assessment_map['marks'] = ''
                
                assessment_list.append(assessment_map)

            module_map['assignment'] = assignment
            module_map['test'] = test
            if assignment > 0:
                assignment_avg = assignment / count_assignments
            if test > 0:
                test_avg = test / count_tests
                
            module_map['assessments'] = assessment_list
            module_map['test_avg'] =  test_avg
            module_map['assignment_avg'] = assignment_avg

            #calculate the percentage

            assignment_percentage = (assignment_avg * module.module.assignment_weight)/100
            test_percentage = (test_avg * module.module.test_weight)/100

            module_map['assignment_percentage'] = assignment_percentage
            module_map['test_percentage'] = test_percentage

            module_map['formative_mark'] = decimal.Decimal(assignment_percentage) + decimal.Decimal(test_percentage)

            module_list.append(module_map)

        return module_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        context['learning_programme'] = registration.student_learning_programme.learning_programme
        
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['procedures'] = registration.registration_period.cohort_period_procedures.all()
        context['reg_active'] = '--active'
        
        return context
    


class StudentLearningProgrammeRegistrationModuleUnitsList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/registered_module_units.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationModuleUnitsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return LearningProgrammeModuleStudyUnit.objects.filter(module_id = self.kwargs['module_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        context['module'] = LearningProgrammeModule.objects.get(id = self.kwargs['module_pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        
        context['learning_programme'] = registration.student_learning_programme.learning_programme
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['procedures'] = registration.registration_period.cohort_period_procedures.all()
        context['reg_active'] = '--active'
        
        return context
    


class StudentLearningProgrammeRegistrationModuleAssessmentsList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/registered_modules_assessments.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationModuleAssessmentsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return StudentRegistrationModuleAssessments.objects.filter(student_registration_module_id = self.kwargs['module_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        context['module'] = StudentRegistrationModule.objects.get(id = self.kwargs['module_pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        
        context['learning_programme'] = registration.student_learning_programme.learning_programme
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['reg_active'] = '--active'
        
        return context
    


class StudentLearningProgrammeRegistrationModuleRegisterList(LoginRequiredMixin,ListView):
    template_name = 'students/learning_programme/registered_modules_register_list.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StudentLearningProgrammeRegistrationModuleRegisterList, self).get(*args, **kwargs)

    def get_queryset(self):
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        register_list = []
        registers = CohortRegistrationPeriodModuleRegister.objects.filter(module = self.kwargs['module_pk'])
        #check what has been added
        for r in registers:
            map_register = {'register':r}
            #check if added
            check_added = CohortRegistrationPeriodModuleRegisterStudents.objects.filter(register=r,student=registration)
            if check_added.exists():
                map_register['student'] = check_added.first()
            else:
                map_register['student'] = None

            register_list.append(map_register)

        return register_list


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = StudentLearningProgrammeRegistration.objects.get(id = self.kwargs['pk'])
        context['module'] = CohortRegistrationPeriodModule.objects.get(id = self.kwargs['module_pk'])
        period = registration.registration_period.period.period
        student = registration.student_learning_programme.student
        
        context['learning_programme'] = registration.student_learning_programme.learning_programme
        context['registration'] = registration
        context['period'] = period
        context['student'] = student
        context['reg_active'] = '--active'
        
        return context
    

@login_required()
def student_learning_programme_registrations_module_register_sign(request,pk,module_pk,register_pk):
    if (request.user.logged_in_role_id == 10):
        #check if the register is signed
        check_register = (CohortRegistrationPeriodModuleRegisterStudents.
                          objects.
                          filter(register_id=register_pk,
                                 student_id=pk).
                          exists())
        
        if not check_register:
            (CohortRegistrationPeriodModuleRegisterStudents.
                          objects.
                          create(register_id=register_pk,
                                 student_id=pk))
            messages.success(request,'Successfully marked your attendance')

        return redirect('students:student_learning_programme_registrations_module_registers',pk=pk,module_pk=module_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')    
    
''''
lecturer views
'''

@login_required()
def lecturer_learning_programme_cohort_students(request,pk,period_pk):
    
    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:

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

                
        return render(request,'students/lecturer/period_registered_students.html',{'students':student_list,
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'cohort_menu':'--active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')







@login_required()
def lecturer_learning_programme_cohort_students_view_wil_procedures(request,pk):
    
    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:

        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        
        fetch_lecturer_procedures = list(CohortRegistrationProcedure.
                                     objects.
                                     filter(lecturer = request.user,
                                            cohort_registration_period = student_registration.registration_period).
                                     values_list('procedure_id', flat=True))
        
       
        logsheet = StudentLogSheet.objects.filter(registration = student_registration,
                                                  procedure_id__in = fetch_lecturer_procedures)
            
                
        return render(request,'students/lecturer/period_registered_students_wil_procedures.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'logsheet':logsheet,
                                                                          'cohort_menu':'--active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    

    
    

    

@login_required()
def lecturer_learning_programme_cohort_procedure_student_attendance(request,pk,procedure_pk):
    
    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedure.objects.get(id = procedure_pk)
        procedures = CohortRegistrationProcedure.objects.filter(cohort_registration_period = learning_programme_cohort_period)
        student_list = list(StudentLearningProgrammeRegistration.
                    objects.
                    filter(student_learning_programme__learning_programme_cohort = learning_programme_cohort,
                           registration_period = learning_programme_cohort_period).
                    values('id',
                           'student_learning_programme__student__first_name',
                           'student_learning_programme__student__last_name',
                           'student_learning_programme__student__email',
                           'student_learning_programme__student__cellphone',
                           'student_learning_programme__student__student_number',))   
        
        time_choices = [                                    
                                    '07:00',
                                    '08:00',
                                    '09:00',
                                    '10:00',
                                    '11:00',
                                    '12:00',
                                    '13:00',
                                    '14:00',
                                    '15:00',
                                    '16:00',
                                    '17:00',
                                    '18:00',                                    
                                ]     
             
        return render(request,'students/lecturer/procedure_attendance.html',{'students':student_list,
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'cohort_menu':'--active',
                                                                          'procedure':procedure,
                                                                          'procedures':procedures,
                                                                          'time_choices':time_choices})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def lecturer_learning_programme_cohort_procedure_student_attendance_save(request,pk):
    
    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedure.objects.get(id = request.POST['procedure'])
        
        #dayshift and SIM block
        shift,block = None,None
        
        competent = ''
        
        if 'competent' in request.POST and request.POST['competent'] != "":
            competent = request.POST['competent']
            
        
        shift_check = ShiftType.objects.filter(shift = 'Day')
        if shift_check.exists():
            shift = shift_check.first()
            
        block_check = ProgarmmeBlock.objects.filter(block_code = 'SIM')
        if block_check.exists():
            block = block_check.first()
        
        form = SIMProcedureLogForm(request.POST)
        if form.is_valid():
            sim_log = form.save(commit=False)
            sim_log.procedure = procedure
            sim_log.registration_period = learning_programme_cohort_period
            sim_log.added_by = request.user
            sim_log.save()
            
            messages.success(request,'Successfully added SIM Procedure Log')
            
            #add the learner attendance logsheet
            students = request.POST.getlist('students_selected[]')
            for s_id in students:
                student = StudentLearningProgrammeRegistration.objects.get(id = s_id)
                StudentLogSheet.objects.create(
                    registration = student,
                    sim_procedure_log = sim_log,
                    start = sim_log.start,
                    end = sim_log.end,
                    date = sim_log.date,
                    end_date = sim_log.date,
                    cohort_procedure = procedure,
                    shift = shift,
                    block = block,
                    competent = competent,
                    attendance_type = "Demonstration",             
                )
        else:
            messages.warning(request,'form.errors')
        
               
        return redirect('students:lecturer_learning_programme_cohort_procedure_student_attendance',pk=pk,procedure_pk=request.POST['procedure'])

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class LecturerLearningProgrammeCohortProcedureGroupAttendanceList(LoginRequiredMixin,ListView):
    template_name = 'students/lecturer/procedure_asessment_group.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortProcedureGroupAttendanceList, self).get(*args, **kwargs)

    def get_queryset(self):
        return SIMProcedureLog.objects.filter(procedure_id = self.kwargs['procedure_pk'],
                                            registration_period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedure.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure
        
        context['cohort_menu'] = '--active'
        
        return context
    
   
   

class LecturerLearningProgrammeCohortProcedureAssessmentAttendanceList(LoginRequiredMixin,ListView):
    template_name = 'students/lecturer/procedure_assessment_attendance.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortProcedureAssessmentAttendanceList, self).get(*args, **kwargs)

    def get_queryset(self):
        return SIMProcedureLog.objects.filter(procedure_id = self.kwargs['procedure_pk'],
                                            registration_period_id = self.kwargs['pk'],
                                            attendance_type = 'Assessment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedure.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure
        
        context['cohort_menu'] = '--active'
        
        return context
    
 
  
class LecturerLearningProgrammeCohortProcedureStudentAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/lecturer/procedure_assessment_group_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortProcedureStudentAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        return list(StudentLogSheet.
                    objects.
                    filter(sim_procedure_log_id = self.kwargs['pk']).
                    values('registration__student_learning_programme__student__first_name',
                           'registration__student_learning_programme__student__last_name',
                           'registration__student_learning_programme__student__student_number',
                           'registration__student_learning_programme__student__email',
                           'registration__student_learning_programme__student__cellphone',
                           'competent',
                           'registration_id',
                           'id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        sim_log = SIMProcedureLog.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort_period = sim_log.registration_period
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = sim_log.procedure
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure
        context['sim_log'] = sim_log
        
        context['cohort_menu'] = '--active'
        
        return context
    



 
 
@login_required()
def lecturer_learning_programme_cohort_procedure_student_attendance_group_students_competency(request,pk):
    
    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
        
        students = request.POST.getlist('students_selected[]')
        for s_id in students:
            student_log = StudentLogSheet.objects.get(id = s_id)
            if 'competent' in request.POST:
                student_log.competent = request.POST['competent']
            student_log.save()
            
        messages.success(request,'Successfully updated competency')        
               
        return redirect('students:lecturer_learning_programme_cohort_procedure_student_attendance_group_students',pk=pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
#Formative Assessments

@login_required()
def lecturer_learning_programme_cohort_module_student_assessment_list(request,pk,module_pk,assessment_pk):
    
    if request.user.logged_in_role_id == 4:
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        assessment = CohortRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
        module = CohortRegistrationPeriodModule.objects.get(id = module_pk)
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme

        students = list(module.
                        students.
                        all().
                        values(
                            'registration__student_learning_programme__student__first_name',
                            'registration__student_learning_programme__student__last_name',
                            'registration__student_learning_programme__student__student_number',
                            'registration__student_learning_programme__student__email',
                            'registration__student_learning_programme__student__cellphone',
                            'registration_id',
                            'id'
                           )
                        )

        student_list = []
        
        for student in students:
            #check if an assessment has been added for the student
            student_map = {'student':student}
            check_assessment = StudentRegistrationModuleAssessments.objects.filter(student_registration_module_id=student['id'],
                                                                                   assessment = assessment)
            if check_assessment.exists():
                fetched_assessment = check_assessment.first()
                student_map['assessment'] = fetched_assessment
            else:
                student_map['assessment'] = None

            student_list.append(student_map)
       
               
        return render(request,'students/lecturer/module_assessment_group_students.html',{'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                                         'module':module,
                                                                                         'students':student_list,
                                                                                         'assessment':assessment,
                                                                                         'cohort_menu':'--active',
                                                                                         'learning_programme_cohort':learning_programme_cohort,
                                                                                         'learning_programme':learning_programme,
                                                                                         })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def lecturer_learning_programme_cohort_module_student_assessment_save(request,pk,assessment_pk):
    
    if request.user.logged_in_role_id == 4:
        
        assessment = CohortRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
        student = StudentRegistrationModule.objects.get(id = pk)

        #check if assessment exists
        check_assessment = StudentRegistrationModuleAssessments.objects.filter(student_registration_module=student,
                                                                                   assessment = assessment)
        
        if check_assessment.exists():
            student_assessment = check_assessment.first()
            student_assessment.marks = request.POST['marks']
            student_assessment.save()
            messages.success(request,'Successfully updated Marks')
        else:
            StudentRegistrationModuleAssessments.objects.create(student_registration_module=student,
                                                                assessment = assessment,
                                                                marks = request.POST['marks'])
            messages.success(request,'Successfully added Marks')

        
        return render(request,'messages.html',)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def lecturer_learning_programme_cohort_module_students(request,pk,module_pk):
    
    if request.user.logged_in_role_id == 4:
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        module = CohortRegistrationPeriodModule.objects.get(id = module_pk)
        assessments = module.formative.all()
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme

        students = list(module.
                        students.
                        all().
                        values(
                            'registration__student_learning_programme__student__first_name',
                            'registration__student_learning_programme__student__last_name',
                            'registration__student_learning_programme__student__student_number',
                            'registration__student_learning_programme__student__email',
                            'registration__student_learning_programme__student__cellphone',
                            'registration_id',
                            'id',
                            'year_mark',
                           )
                        )

        student_list = []
        
        for student in students:
            #check if an assessment has been added for the student
            student_map = {'student':student}
            
            assessment_list = []
            assignment = 0
            count_assignments = 0
            test = 0
            count_tests = 0
            assignment_avg = 0
            test_avg = 0
            assignment_percentage,test_percentage = 0,0
            for assessment in assessments:
                if assessment.assessment_type == 'Assignment':
                    count_assignments = count_assignments + 1
                else:
                    count_tests = count_tests + 1

                assessment_map = {'assessment':assessment}
                check_assessment = StudentRegistrationModuleAssessments.objects.filter(student_registration_module_id=student['id'],
                                                                                   assessment = assessment)
                if check_assessment.exists():
                    fetched_assessment = check_assessment.first()
                    assessment_map['marks'] = fetched_assessment.marks
                    if fetched_assessment.marks != None:
                        if assessment.assessment_type == 'Assignment':
                            assignment = assignment + fetched_assessment.marks
                        else:
                            test = test + fetched_assessment.marks
                else:
                    assessment_map['marks'] = ''
                
                assessment_list.append(assessment_map)

            student_map['assignment'] = assignment
            student_map['test'] = test
            if assignment > 0:
                assignment_avg = assignment / count_assignments
            if test > 0:
                test_avg = test / count_tests
                
            student_map['assessments'] = assessment_list
            student_map['test_avg'] =  test_avg
            student_map['assignment_avg'] = assignment_avg

            #calculate the percentage

            assignment_percentage = (assignment_avg * module.assignment_weight)/100
            test_percentage = (test_avg * module.test_weight)/100

            student_map['assignment_percentage'] = assignment_percentage
            student_map['test_percentage'] = test_percentage

            student_map['formative_mark'] = decimal.Decimal(assignment_percentage) + decimal.Decimal(test_percentage)
            
         
            student_list.append(student_map)

        return render(request,'students/lecturer/module_group_students.html',{'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                                         'module':module,
                                                                                         'students':student_list,
                                                                                         'assessments':assessments,
                                                                                         'cohort_menu':'--active',
                                                                                         'learning_programme_cohort':learning_programme_cohort,
                                                                                         'learning_programme':learning_programme,
                                                                                         })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def lecturer_learning_programme_cohort_module_student_assessment_list(request,pk,module_pk,assessment_pk):
    
    if request.user.logged_in_role_id == 4:
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        assessment = CohortRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
        module = CohortRegistrationPeriodModule.objects.get(id = module_pk)
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme

        students = list(module.
                        students.
                        all().
                        values(
                            'registration__student_learning_programme__student__first_name',
                            'registration__student_learning_programme__student__last_name',
                            'registration__student_learning_programme__student__student_number',
                            'registration__student_learning_programme__student__email',
                            'registration__student_learning_programme__student__cellphone',
                            'registration_id',
                            'id'
                           )
                        )

        student_list = []
        
        for student in students:
            #check if an assessment has been added for the student
            student_map = {'student':student}
            check_assessment = StudentRegistrationModuleAssessments.objects.filter(student_registration_module_id=student['id'],
                                                                                   assessment = assessment)
            if check_assessment.exists():
                fetched_assessment = check_assessment.first()
                student_map['assessment'] = fetched_assessment
            else:
                student_map['assessment'] = None

            student_list.append(student_map)
       
               
        return render(request,'students/lecturer/module_assessment_group_students.html',{'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                                         'module':module,
                                                                                         'students':student_list,
                                                                                         'assessment':assessment,
                                                                                         'cohort_menu':'--active',
                                                                                         'learning_programme_cohort':learning_programme_cohort,
                                                                                         'learning_programme':learning_programme,
                                                                                         })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def lecturer_learning_programme_cohort_module_student_assessment_save(request,pk,assessment_pk):
    
    if request.user.logged_in_role_id == 4:
        
        assessment = CohortRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
        student = StudentRegistrationModule.objects.get(id = pk)
        module = assessment.module

        #check if assessment exists
        check_assessment = StudentRegistrationModuleAssessments.objects.filter(student_registration_module=student,
                                                                                   assessment = assessment)
        
        if check_assessment.exists():
            student_assessment = check_assessment.first()
            student_assessment.marks = request.POST['marks']
            student_assessment.save()
            messages.success(request,'Successfully updated Marks')
        else:
            StudentRegistrationModuleAssessments.objects.create(student_registration_module=student,
                                                                assessment = assessment,
                                                                marks = request.POST['marks'])
            messages.success(request,'Successfully added Marks')
            
        assessments = module.formative.all()
        
        count_assignments,count_tests,assignment,test = 0,0,0,0

        for assessment in assessments:
            if assessment.assessment_type == 'Assignment':
                count_assignments = count_assignments + 1
            else:
                count_tests = count_tests + 1

            check_assessment = StudentRegistrationModuleAssessments.objects.filter(student_registration_module=student,
                                                                                assessment = assessment)
            if check_assessment.exists():
                fetched_assessment = check_assessment.first()
                if fetched_assessment.marks != None:
                    if assessment.assessment_type == 'Assignment':
                        assignment = assignment + fetched_assessment.marks
                    else:
                        test = test + fetched_assessment.marks
            
        if assignment > 0:
            assignment_avg = assignment / count_assignments
        if test > 0:
            test_avg = test / count_tests

        assignment_percentage = (assignment_avg * module.assignment_weight)/100
        test_percentage = (test_avg * module.test_weight)/100
        assignment_percentage = assignment_percentage
        test_percentage = test_percentage
        formative_mark = decimal.Decimal(assignment_percentage) + decimal.Decimal(test_percentage)

        student.year_mark = formative_mark
        student.save()
        
                
        return render(request,'messages.html',)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
'''
Summative Assessments
'''

@login_required()
def lecturer_learning_programme_cohort_module_summative_student_assessment_list(request,pk,module_pk):
    
    if request.user.logged_in_role_id == 4:
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        module = CohortRegistrationPeriodModule.objects.get(id = module_pk)
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme

        students = list(StudentRegistrationModule.
                        objects.
                        filter(module = module).
                        values(
                            'registration__student_learning_programme__student__first_name',
                            'registration__student_learning_programme__student__last_name',
                            'registration__student_learning_programme__student__student_number',
                            'registration__student_learning_programme__student__email',
                            'registration__student_learning_programme__student__cellphone',
                            'registration_id',
                            'id',
                            'summative_assessor1',
                            'summative_assessor2',
                            'year_mark',
                           )
                        )
               
        return render(request,'students/lecturer/module_summative_assessment_group_students.html',{'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                                         'module':module,
                                                                                         'students':students,
                                                                                         'cohort_menu':'--active',
                                                                                         'learning_programme_cohort':learning_programme_cohort,
                                                                                         'learning_programme':learning_programme,
                                                                                         })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def lecturer_learning_programme_cohort_module_summative_student_assessment_save(request,pk,assessor):
    
    if request.user.logged_in_role_id == 4:
        
        student = StudentRegistrationModule.objects.get(id = pk)

        if assessor == 1:
            student.summative_assessor1 = request.POST['marks']
        elif assessor == 2:
            student.summative_assessor2 = request.POST['marks']

        student.save()

        if student.summative_assessor1 and student.summative_assessor2:
            student.final_mark = (int(student.summative_assessor1) + int(student.summative_assessor2))/2
        student.save()
        
        students = list(StudentRegistrationModule.
                        objects.
                        filter(module = student.module).
                        values(
                            'registration__student_learning_programme__student__first_name',
                            'registration__student_learning_programme__student__last_name',
                            'registration__student_learning_programme__student__student_number',
                            'registration__student_learning_programme__student__email',
                            'registration__student_learning_programme__student__cellphone',
                            'registration_id',
                            'id',
                            'summative_assessor1',
                            'summative_assessor2',
                            'year_mark',
                           )
                        )

        messages.success(request,'Successfully added Marks')

        
        return render(request,'students/lecturer/partials/module_summative_assessment_group_students.html',
                      { 'learning_programme_cohort_period':student.registration.registration_period,
                        'module':student.module,
                        'students':students,
                        'cohort_menu':'--active',
                        'learning_programme_cohort':student.registration.registration_period.learning_programme_cohort,
                        'learning_programme':student.registration.registration_period.learning_programme_cohort.learning_programme,
                      })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


''''
NEW ASSESSMENT VIEWS
'''

#####FORMATIVE ASSESSMENTS

class LecturerLearningProgrammeCohortProcedureStudentFormativeAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/lecturer/procedure_assessment_formative_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortProcedureStudentFormativeAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        registrations =  (StudentLearningProgrammeRegistration.
                    objects.
                    filter(registration_period_id = self.kwargs['pk']).
                    only('student_learning_programme__student__student_number',
                         'student_learning_programme__student__first_name',
                         'student_learning_programme__student__last_name',
                         'student_learning_programme__student__email',
                         'id'))
        
        students = []
        for reg in registrations:
            stud_map = {'student':reg}
            stud_map['attempts'] = (StudentProcedureFormativeAssessmentAttempt.
                                    objects.
                                    filter(student_procedure_formative__registration = reg,
                                           cohort_procedure_id = self.kwargs['procedure_pk']).
                                    only('attempt','id'))
            
            students.append(stud_map)

        return students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedure.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure        
        context['cohort_menu'] = '--active'
        
        return context
    
    

class CoAssessorLearningProgrammeCohortProcedureStudentFormativeAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/coassessor/procedure_assessment_formative_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 12:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CoAssessorLearningProgrammeCohortProcedureStudentFormativeAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        registrations =  (StudentLearningProgrammeRegistration.
                    objects.
                    filter(registration_period_id = self.kwargs['pk']).
                    only('student_learning_programme__student__student_number',
                         'student_learning_programme__student__first_name',
                         'student_learning_programme__student__last_name',
                         'student_learning_programme__student__email',
                         'id'))
        
        students = []
        for reg in registrations:
            stud_map = {'student':reg}
            stud_map['attempts'] = (StudentProcedureFormativeAssessmentAttempt.
                                    objects.
                                    filter(student_procedure_formative__registration = reg,
                                           cohort_procedure_id = self.kwargs['procedure_pk']).
                                    only('attempt','id'))
            
            students.append(stud_map)

        return students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedure.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure        
        context['cohort_menu'] = '--active'
        
        return context
    

class ProgrammeCoordinatorLearningProgrammeCohortProcedureStudentFormativeAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/programme_coordinator/procedure_assessment_formative_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ProgrammeCoordinatorLearningProgrammeCohortProcedureStudentFormativeAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        procedure = CohortRegistrationProcedure.objects.get(id = self.kwargs['procedure_pk'])
        assessor = procedure.lecturer
        clinical_facilitator = procedure.clinical_facilitator
        co_assessor = procedure.co_assessor
        
        
        registrations =  (StudentLearningProgrammeRegistration.
                    objects.
                    filter(registration_period_id = self.kwargs['pk']).
                    only('student_learning_programme__student__student_number',
                         'student_learning_programme__student__first_name',
                         'student_learning_programme__student__last_name',
                         'student_learning_programme__student__email',
                         'id'))
        
        students = []
        for reg in registrations:
            stud_map = {'student':reg}
            final_mark = StudentProcedureFormative.objects.filter(registration = reg,cohort_procedure_id = self.kwargs['procedure_pk']).only('final_mark').first()
            if final_mark:
                stud_map['final_mark'] = final_mark.final_mark
            else:
                stud_map['final_mark'] = '-'
            stud_map['attempts_assessor'] = (StudentProcedureFormativeAssessment.
                                    objects.
                                    filter(attempt__student_procedure_formative__registration = reg,
                                           attempt__cohort_procedure_id = self.kwargs['procedure_pk'],
                                           assessor = assessor,
                                           ).
                                    only('attempt__attempt','id','attempt__id'))
            
            stud_map['attempts_cf'] = (StudentProcedureFormativeAssessment.
                                    objects.
                                    filter(attempt__student_procedure_formative__registration = reg,
                                           attempt__cohort_procedure_id = self.kwargs['procedure_pk'],
                                           assessor = clinical_facilitator,
                                           ).
                                    only('attempt__attempt','id','attempt__id'))
            
            stud_map['attempts_coassessor'] = (StudentProcedureFormativeAssessment.
                                    objects.
                                    filter(attempt__student_procedure_formative__registration = reg,
                                           attempt__cohort_procedure_id = self.kwargs['procedure_pk'],
                                           assessor = co_assessor,
                                           ).
                                    only('attempt__attempt','id','attempt__id'))
            
            students.append(stud_map)

        return students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedure.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure        
        context['cohort_menu'] = '--active'
        
        return context
    
    
@login_required()
def lecturer_learning_programme_cohort_procedure_formative_student_attempt_add(request,pk,procedure_pk):
    
    if request.user.logged_in_role_id == 6:

        procedure = CohortRegistrationProcedure.objects.get(id = procedure_pk)
        
        students = request.POST.getlist('students_selected[]')
        for s_id in students:
            #check if procedure added
            
            check_student_procedure = StudentProcedureFormative.objects.filter(registration_id = s_id,
                                                                      cohort_procedure = procedure)
            if check_student_procedure.exists():
                student_procedure = check_student_procedure.first()
            else:
                student_procedure = StudentProcedureFormative.objects.create(registration_id = s_id,
                                                                      cohort_procedure = procedure)
                
                
            #cehck if attempt is there
            check_attempt = StudentProcedureFormativeAssessmentAttempt.objects.filter(attempt = request.POST['attempt'],
                                                                      student_procedure_formative = student_procedure,
                                                                      cohort_procedure = procedure)
            
            if not check_attempt.exists():        
                StudentProcedureFormativeAssessmentAttempt.objects.create(attempt = request.POST['attempt'],
                                                                      cohort_procedure = procedure,
                                                                      student_procedure_formative = student_procedure)
            else:
                attempt = check_attempt.first()
                attempt.student_procedure_formative = student_procedure
                attempt.save()
            
        messages.success(request,'Successfully added attempt')        
               
        return redirect('students:programme_coordinator_learning_programme_cohort_procedure_student_formative_assessment_list',pk=pk,procedure_pk=procedure_pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
 
 

@login_required()
def programme_coordinator_learning_programme_cohort_students_view_wil_procedures_assessment(request,pk,attempt_pk):
    
    if request.user.logged_in_role_id == 6:

        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        attempt_user = StudentProcedureFormativeAssessment.objects.get(id = attempt_pk)
        procedure_entry = attempt_user.attempt.cohort_procedure
        
        
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        
        assessment = []
        
        total_marks = 0
        
        total = 0

        total_marks_percentage = 0

        
        assessments = list(CohortRegistrationProcedureTaskAssessment.
                           objects.
                           filter(
                               task = procedure_entry, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        
        penalty = 0
       
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
            
            check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']
            
            assessment.append(ass_map)

        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty

        return render(request,'students/programme_coordinator/period_registered_students_wil_procedure_assessment.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'procedure_entry':attempt_user,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,
                                                                          'total_marks':total_marks,
                                                                          'total_marks_percentage':total_marks_percentage,
                                                                          'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                                                                           'penalty':penalty,
                                                                          'total':total,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



   
@login_required()
def lecturer_learning_programme_cohort_students_view_wil_procedures_assessment(request,pk,attempt_pk):
    
    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:

        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        attempt = StudentProcedureFormativeAssessmentAttempt.objects.get(id = attempt_pk)
        procedure_entry = attempt.cohort_procedure
        
        
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        
        assessment = []
        
        total_marks = 0
        
        total = 0

        total_marks_percentage = 0

        #check if attempt for the user exists, if it doesn't then add it

        check_attempt_user = StudentProcedureFormativeAssessment.objects.filter(attempt = attempt,assessor=request.user)

        if check_attempt_user.exists():
            attempt_user = check_attempt_user.first()
        else:
            attempt_user = StudentProcedureFormativeAssessment.objects.create(attempt = attempt,assessor=request.user)
        
        assessments = list(CohortRegistrationProcedureTaskAssessment.
                           objects.
                           filter(
                               task = procedure_entry, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
            
            check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']

            assessment.append(ass_map)

        
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty
            
            

        return render(request,'students/lecturer/period_registered_students_wil_procedure_assessment.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'procedure_entry':attempt_user,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,
                                                                          'total_marks':total_marks,
                                                                          'total_marks_percentage':total_marks_percentage,
                                                                          'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                                                                           'penalty':penalty,
                                                                          'total':total,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


   
@login_required()
def co_assessor_learning_programme_cohort_students_view_wil_procedures_assessment(request,pk,attempt_pk):
    
    if request.user.logged_in_role_id == 12:

        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        attempt = StudentProcedureFormativeAssessmentAttempt.objects.get(id = attempt_pk)
        procedure_entry = attempt.cohort_procedure
        
        
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        
        assessment = []
        
        total_marks = 0
        
        total = 0

        total_marks_percentage = 0

        #check if attempt for the user exists, if it doesn't then add it

        check_attempt_user = StudentProcedureFormativeAssessment.objects.filter(attempt = attempt,assessor=request.user)

        if check_attempt_user.exists():
            attempt_user = check_attempt_user.first()
        else:
            attempt_user = StudentProcedureFormativeAssessment.objects.create(attempt = attempt,assessor=request.user)
        
        assessments = list(CohortRegistrationProcedureTaskAssessment.
                           objects.
                           filter(
                               task = procedure_entry, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
            
            check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']

            assessment.append(ass_map)

        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty

        return render(request,'students/coassessor/period_registered_students_wil_procedure_assessment.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'procedure_entry':attempt_user,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,
                                                                          'total_marks':total_marks,
                                                                          'total_marks_percentage':total_marks_percentage,
                                                                          'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                                                                           'penalty':penalty,
                                                                          'total':total,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def save_procedure_answer(request,pk,attempt_pk,assessment_pk):
    '''
    save answer
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 12:
        
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        

        assessment = (CohortRegistrationProcedureTaskAssessment.
                           objects.
                           get(
                               id = assessment_pk                              
                           ))
        
        #check if assessment exists:
        check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                ))
        
        if check_answer.exists():
            answer = check_answer.first()
            answer.answer = request.GET['answer']
            answer.save()
            messages.success(request,'Successfully edited competency')
        else:
            answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                create(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                    answer = request.GET['answer']
                                ))
            messages.success(request,'Successfully added competency')
            
        attempt_user = answer.attempt
            
        assessment = []
        
        total = 0
        total_marks = 0
        total_marks_percentage = 0
        
        assessments = list(CohortRegistrationProcedureTaskAssessment.
                           objects.
                           filter(
                               task = attempt_user.attempt.cohort_procedure, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
                           
            check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']
                    
            assessment.append(ass_map)
            
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty
            
        return render(request,
                      'students/lecturer/partials/period_registered_students_wil_procedure_assessment.html',
                      { 'assessment':assessment,
                        'learning_programme_cohort':learning_programme_cohort,
                        'learning_programme':learning_programme,
                        'learning_programme_cohort_period':learning_programme_cohort_period,
                        'student_registration':student_registration,
                        'procedure_entry':attempt_user,
                        'total_marks':total_marks,
                        'total':total,
                        'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                        'penalty':penalty,
                        'total_marks_percentage':total_marks_percentage,
                       })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        
@login_required()
def save_procedure_comment(request,pk,attempt_pk,assessment_pk):
    '''
    save comment
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 12:
        
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        

        assessment = (CohortRegistrationProcedureTaskAssessment.
                           objects.
                           get(
                               id = assessment_pk                              
                           ))
        
        #check if assessment exists:
        check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                ))
        
        if check_answer.exists():
            answer = check_answer.first()
            answer.comment = request.GET['comment']
            answer.save()
            messages.success(request,'Successfully edited comment')
        else:
            answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                create(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                    comment = request.GET['comment']
                                ))
            messages.success(request,'Successfully added comment')
            
        attempt_user = answer.attempt
            
        assessment = []
        
        total = 0
        total_marks = 0
        
        assessments = list(CohortRegistrationProcedureTaskAssessment.
                           objects.
                           filter(
                               task = attempt_user.attempt.cohort_procedure, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
       
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
                           
            check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    
                    total_marks = total_marks - ass['penalty']
                    
            
            
            assessment.append(ass_map)
            
        return render(request,
                      'messages.html',)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def process_procedure_formative_assessment_final_mark(request,pk,attempt_pk):
    '''
    Process the final mark
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 12:
        
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
          
        attempt_user = StudentProcedureFormativeAssessment.objects.get(id = attempt_pk)
            
        assessment = []
        
        total = 0
        total_marks = 0
        total_marks_percentage = 0

        all_questions_answered = True
        
        assessments = list(CohortRegistrationProcedureTaskAssessment.
                           objects.
                           filter(
                               task = attempt_user.attempt.cohort_procedure, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
                           
                check_answer = (StudentProcedureFormativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
                if check_answer.exists():
                    answer = check_answer.first()
                
                    ass_map['answer_id'] = answer.id
                    ass_map['answer_answer'] = answer.answer
                    ass_map['answer_comment'] = answer.comment
                    
                    if ass_map['answer_answer'] == 'Competent':
                        total_marks = total_marks + 1
                        total_marks_percentage = round((total_marks/total)*100)
                    elif ass_map['answer_answer'] == 'Not Applicable':
                        total = total - 1
                    elif ass_map['answer_answer'] == 'Not Yet Competent':
                        penalty = penalty + ass['penalty']

                else:
                    all_questions_answered = False
                    
            assessment.append(ass_map)
            
        
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty
        
        if all_questions_answered:
            attempt_user.assessor_mark = total_marks_percentage
            attempt_user.save()
            messages.success(request,"Final Mark Processed and Saved")
        else:
            messages.warning(request,"Marks not Processed, all questions need to be marked")
            
        if request.user.logged_in_role_id == 12:
            return render(request,
                      'students/coassessor/period_registered_students_wil_procedure_assessment.html',
                      { 'assessment':assessment,
                        'learning_programme_cohort':learning_programme_cohort,
                        'learning_programme':learning_programme,
                        'learning_programme_cohort_period':learning_programme_cohort_period,
                        'student_registration':student_registration,
                        'procedure_entry':attempt_user,
                        'total_marks':total_marks,
                        'total':total,
                        'total_marks_percentage':total_marks_percentage,
                        'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                        'penalty':penalty,
                       })
        else:
            return render(request,
                      'students/lecturer/period_registered_students_wil_procedure_assessment.html',
                      { 'assessment':assessment,
                        'learning_programme_cohort':learning_programme_cohort,
                        'learning_programme':learning_programme,
                        'learning_programme_cohort_period':learning_programme_cohort_period,
                        'student_registration':student_registration,
                        'procedure_entry':attempt_user,
                        'total_marks':total_marks,
                        'total':total,
                        'total_marks_percentage':total_marks_percentage,
                        'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                        'penalty':penalty,
                       })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

#####SUMMATIVE ASSESSMENTS


class LecturerLearningProgrammeCohortProcedureStudentSummativeAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/lecturer/procedure_assessment_summative_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortProcedureStudentSummativeAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        registrations =  (StudentLearningProgrammeRegistration.
                    objects.
                    filter(registration_period_id = self.kwargs['pk']).
                    only('student_learning_programme__student__student_number',
                         'student_learning_programme__student__first_name',
                         'student_learning_programme__student__last_name',
                         'student_learning_programme__student__email',
                         'id'))
        
        students = []
        for reg in registrations:
            stud_map = {'student':reg}
            stud_map['attempts'] = (StudentProcedureSummativeAssessmentAttempt.
                                    objects.
                                    filter(student_procedure_summative__registration = reg,
                                           cohort_procedure_id = self.kwargs['procedure_pk']).
                                    only('attempt','id'))
            
            students.append(stud_map)

        return students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedureSummative.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure        
        context['cohort_menu'] = '--active'
        
        return context



class CoAssessorLearningProgrammeCohortProcedureStudentSummativeAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/coassessor/procedure_assessment_summative_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 12:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CoAssessorLearningProgrammeCohortProcedureStudentSummativeAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        registrations =  (StudentLearningProgrammeRegistration.
                    objects.
                    filter(registration_period_id = self.kwargs['pk']).
                    only('student_learning_programme__student__student_number',
                         'student_learning_programme__student__first_name',
                         'student_learning_programme__student__last_name',
                         'student_learning_programme__student__email',
                         'id'))
        
        students = []
        for reg in registrations:
            stud_map = {'student':reg}
            stud_map['attempts'] = (StudentProcedureSummativeAssessmentAttempt.
                                    objects.
                                    filter(student_procedure_summative__registration = reg,
                                           cohort_procedure_id = self.kwargs['procedure_pk']).
                                    only('attempt','id'))
            
            students.append(stud_map)

        return students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedureSummative.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure        
        context['cohort_menu'] = '--active'
        
        return context
    
    

class ModeratorLearningProgrammeCohortProcedureStudentSummativeAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/moderator/procedure_assessment_summative_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 7:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ModeratorLearningProgrammeCohortProcedureStudentSummativeAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        registrations =  (StudentLearningProgrammeRegistration.
                    objects.
                    filter(registration_period_id = self.kwargs['pk']).
                    only('student_learning_programme__student__student_number',
                         'student_learning_programme__student__first_name',
                         'student_learning_programme__student__last_name',
                         'student_learning_programme__student__email',
                         'id'))
        
        students = []
        for reg in registrations:
            stud_map = {'student':reg}
            stud_map['attempts'] = (StudentProcedureSummativeAssessmentAttempt.
                                    objects.
                                    filter(student_procedure_summative__registration = reg,
                                           cohort_procedure_id = self.kwargs['procedure_pk']).
                                    only('attempt','id'))
            
            students.append(stud_map)

        return students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedureSummative.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure        
        context['cohort_menu'] = '--active'
        
        return context



class ProgrammeCoordinatorLearningProgrammeCohortProcedureStudentSummativeAsessmentList(LoginRequiredMixin,ListView):
    template_name = 'students/programme_coordinator/procedure_assessment_summative_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ProgrammeCoordinatorLearningProgrammeCohortProcedureStudentSummativeAsessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        
        procedure = CohortRegistrationProcedureSummative.objects.get(id = self.kwargs['procedure_pk'])
        assessor = procedure.assessor
        co_assessor = procedure.co_assessor
        clinical_facilitator = procedure.clinical_facilitator
        
        registrations =  (StudentLearningProgrammeRegistration.
                    objects.
                    filter(registration_period_id = self.kwargs['pk']).
                    only('student_learning_programme__student__student_number',
                         'student_learning_programme__student__first_name',
                         'student_learning_programme__student__last_name',
                         'student_learning_programme__student__email',
                         'id'))
        
        students = []
        for reg in registrations:
            stud_map = {'student':reg}
            stud_map['attempts_assessor'] = (StudentProcedureSummativeAssessment.
                                    objects.
                                    filter(attempt__student_procedure_summative__registration = reg,
                                           attempt__cohort_procedure_id = self.kwargs['procedure_pk'],
                                           assessor = assessor,
                                           ).
                                    only('attempt__attempt','id','attempt__id'))
            
            stud_map['attempts_cf'] = (StudentProcedureSummativeAssessment.
                                    objects.
                                    filter(attempt__student_procedure_summative__registration = reg,
                                           attempt__cohort_procedure_id = self.kwargs['procedure_pk'],
                                           assessor = clinical_facilitator,
                                           ).
                                    only('attempt__attempt','id','attempt__id'))
            
            stud_map['attempts_coassessor'] = (StudentProcedureSummativeAssessment.
                                    objects.
                                    filter(attempt__student_procedure_summative__registration = reg,
                                           attempt__cohort_procedure_id = self.kwargs['procedure_pk'],
                                           assessor = co_assessor,
                                           ).
                                    only('attempt__attempt','id','attempt__id'))
            
            students.append(stud_map)

        return students


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        procedure = CohortRegistrationProcedureSummative.objects.get(id = self.kwargs['procedure_pk'])
        
        context['learning_programme_cohort_period'] = learning_programme_cohort_period
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['procedure'] = procedure        
        context['cohort_menu'] = '--active'
        
        return context
    
    
@login_required()
def lecturer_learning_programme_cohort_procedure_summative_student_attempt_add(request,pk,procedure_pk):
    
    if request.user.logged_in_role_id == 6:

        procedure = CohortRegistrationProcedureSummative.objects.get(id = procedure_pk)
        
        students = request.POST.getlist('students_selected[]')
        for s_id in students:
            #check if procedure added
            
            check_student_procedure = StudentProcedureSummative.objects.filter(registration_id = s_id,
                                                                      cohort_procedure = procedure)
            if check_student_procedure.exists():
                student_procedure = check_student_procedure.first()
            else:
                student_procedure = StudentProcedureSummative.objects.create(registration_id = s_id,
                                                                      cohort_procedure = procedure)
                
            #cehck if attempt is there
            check_attempt = StudentProcedureSummativeAssessmentAttempt.objects.filter(attempt = request.POST['attempt'],
                                                                      student_procedure_summative = student_procedure,
                                                                      cohort_procedure = procedure)
            
            if not check_attempt.exists():        
                StudentProcedureSummativeAssessmentAttempt.objects.create(attempt = request.POST['attempt'],
                                                                      cohort_procedure = procedure,
                                                                      student_procedure_summative = student_procedure)
            else:
                attempt = check_attempt.first()
                attempt.student_procedure_summative = student_procedure
                attempt.save()
            
        messages.success(request,'Successfully added attempt')        
               
        return redirect('students:programme_coordinator_learning_programme_cohort_procedure_student_summative_assessment_list',pk=pk,procedure_pk=procedure_pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def lecturer_learning_programme_cohort_students_view_wil_procedures_summative_assessment(request,pk,attempt_pk):
    
    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
       
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        attempt = StudentProcedureSummativeAssessmentAttempt.objects.get(id = attempt_pk)
        procedure_entry = attempt.cohort_procedure
        
        
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        learning_programme_cohort_registration_period = student_registration.registration_period

                
        assessment = []
        
        total_marks = 0
        
        total = 0

        total_marks_percentage = 0

        #check if attempt for the user exists, if it doesn't then add it

        check_attempt_user = StudentProcedureSummativeAssessment.objects.filter(attempt = attempt,assessor=request.user)

        if check_attempt_user.exists():
            attempt_user = check_attempt_user.first()
        else:
            attempt_user = StudentProcedureSummativeAssessment.objects.create(attempt = attempt,assessor=request.user)
        
        assessments = list(CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           filter(
                               task = procedure_entry, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
            
            check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']
            
            
            assessment.append(ass_map)
            
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty

        return render(request,'students/lecturer/period_registered_students_wil_procedure_summative_assessment.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'procedure_entry':attempt_user,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,
                                                                          'total_marks':total_marks,
                                                                          'total_marks_percentage':total_marks_percentage,
                                                                          'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                                                                          'penalty':penalty,
                                                                          'learning_programme_cohort_registration_period':learning_programme_cohort_registration_period,
                                                                          'total':total,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def co_assessor_learning_programme_cohort_students_view_wil_procedures_summative_assessment(request,pk,attempt_pk):
    
    if request.user.logged_in_role_id == 12:

        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        attempt = StudentProcedureSummativeAssessmentAttempt.objects.get(id = attempt_pk)
        procedure_entry = attempt.cohort_procedure
        
        
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        learning_programme_cohort_registration_period = student_registration.registration_period
        
        assessment = []
        
        total_marks = 0
        
        total = 0

        total_marks_percentage = 0

        #check if attempt for the user exists, if it doesn't then add it

        check_attempt_user = StudentProcedureSummativeAssessment.objects.filter(attempt = attempt,assessor=request.user)

        if check_attempt_user.exists():
            attempt_user = check_attempt_user.first()
        else:
            attempt_user = StudentProcedureSummativeAssessment.objects.create(attempt = attempt,assessor=request.user)
        
        assessments = list(CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           filter(
                               task = procedure_entry, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
            
            check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']
            
            
            assessment.append(ass_map)
            
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty

        return render(request,'students/coassessor/period_registered_students_wil_procedure_summative_assessment.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'procedure_entry':attempt_user,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,
                                                                          'total_marks':total_marks,
                                                                          'total_marks_percentage':total_marks_percentage,
                                                                          'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                                                                          'penalty':penalty,
                                                                          'learning_programme_cohort_registration_period':learning_programme_cohort_registration_period,
                                                                          'total':total,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def moderator_learning_programme_cohort_students_view_wil_procedures_summative_assessment(request,pk,attempt_pk):
    
    if request.user.logged_in_role_id == 7:

        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        attempt = StudentProcedureSummativeAssessmentAttempt.objects.get(id = attempt_pk)
        procedure_entry = attempt.cohort_procedure
        
        
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        learning_programme_cohort_registration_period = student_registration.registration_period
        
        assessment = []
        
        total_marks = 0
        
        total = 0

        total_marks_percentage = 0

        #check if attempt for the user exists, if it doesn't then add it

        check_attempt_user = StudentProcedureSummativeAssessment.objects.filter(attempt = attempt,assessor=request.user)

        if check_attempt_user.exists():
            attempt_user = check_attempt_user.first()
        else:
            attempt_user = StudentProcedureSummativeAssessment.objects.create(attempt = attempt,assessor=request.user)
        
        assessments = list(CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           filter(
                               task = procedure_entry, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
            
            check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']
            
            
            assessment.append(ass_map)
            
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty

        return render(request,'students/moderator/period_registered_students_wil_procedure_summative_assessment.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'procedure_entry':attempt_user,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,
                                                                          'total_marks':total_marks,
                                                                          'total_marks_percentage':total_marks_percentage,
                                                                          'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                                                                          'penalty':penalty,
                                                                          'learning_programme_cohort_registration_period':learning_programme_cohort_registration_period,
                                                                          'total':total,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def programme_coordinator_learning_programme_cohort_students_view_wil_procedures_summative_assessment(request,pk,attempt_pk):
    
    if request.user.logged_in_role_id == 6:
       
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        attempt_user = StudentProcedureSummativeAssessment.objects.get(id = attempt_pk)
        procedure_entry = attempt_user.attempt.cohort_procedure
        
        
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        learning_programme_cohort_registration_period = student_registration.registration_period

                
        assessment = []
        
        total_marks = 0
        
        total = 0

        total_marks_percentage = 0

        assessments = list(CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           filter(
                               task = procedure_entry, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
            
            check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']
            
            
            assessment.append(ass_map)
            
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty

        return render(request,'students/programme_coordinator/period_registered_students_wil_procedure_summative_assessment.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'student_registration':student_registration,
                                                                          'procedure_entry':attempt_user,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,
                                                                          'total_marks':total_marks,
                                                                          'total_marks_percentage':total_marks_percentage,
                                                                          'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                                                                          'penalty':penalty,
                                                                          'learning_programme_cohort_registration_period':learning_programme_cohort_registration_period,
                                                                          'total':total,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')




@login_required()
def save_procedure_summative_answer(request,pk,attempt_pk,assessment_pk):
    '''
    save answer
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 12 or request.user.logged_in_role_id == 7:
        
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        learning_programme_cohort_registration_period = student_registration.registration_period
        

        assessment = (CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           get(
                               id = assessment_pk                              
                           ))
        
        attempt = StudentProcedureSummativeAssessment.objects.get(id = attempt_pk)
        
        #check if assessment exists:
        check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                ))
        
        if check_answer.exists():
            answer = check_answer.first()
            answer.answer = request.GET['answer']
            answer.save()
            messages.success(request,'Successfully edited competency')
        else:
            answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                create(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                    answer = request.GET['answer']
                                ))
            messages.success(request,'Successfully added competency')
            
        attempt_user = answer.attempt
            
        assessment = []
        
        total = 0
        total_marks = 0
        total_marks_percentage = 0
        
        assessments = list(CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           filter(
                               task = attempt_user.attempt.cohort_procedure, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
                           
            check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                    total_marks_percentage = round((total_marks/total)*100)
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    penalty = penalty + ass['penalty']
                    
            assessment.append(ass_map)
            
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty
            
        return render(request,
                      'students/lecturer/partials/period_registered_students_wil_procedure_summative_assessment.html',
                      { 'assessment':assessment,
                        'learning_programme_cohort':learning_programme_cohort,
                        'learning_programme':learning_programme,
                        'learning_programme_cohort_period':learning_programme_cohort_period,
                        'student_registration':student_registration,
                        'procedure_entry':attempt_user,
                        'total_marks':total_marks,
                        'total':total,
                        'learning_programme_cohort_registration_period':learning_programme_cohort_registration_period,
                        'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                        'penalty':penalty,
                        'total_marks_percentage':total_marks_percentage,
                       })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        


@login_required()
def save_procedure_summative_comment(request,pk,attempt_pk,assessment_pk):
    '''
    save comment
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 12 or request.user.logged_in_role_id == 7:
        
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        

        assessment = (CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           get(
                               id = assessment_pk                              
                           ))
        
        #check if assessment exists:
        check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                ))
        
        if check_answer.exists():
            answer = check_answer.first()
            answer.comment = request.GET['comment']
            answer.save()
            messages.success(request,'Successfully edited comment')
        else:
            answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                create(
                                    assessment_id = assessment_pk,
                                    attempt_id = attempt_pk,
                                    comment = request.GET['comment']
                                ))
            messages.success(request,'Successfully added comment')
            
        attempt_user = answer.attempt
            
        assessment = []
        
        total = 0
        total_marks = 0
        
        assessments = list(CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           filter(
                               task = attempt_user.attempt.cohort_procedure, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
       
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
                           
            check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.comment
                
                if ass_map['answer_answer'] == 'Competent':
                    total_marks = total_marks + 1
                elif ass_map['answer_answer'] == 'Not Applicable':
                    total = total - 1
                elif ass_map['answer_answer'] == 'Not Yet Competent':
                    total_marks = total_marks - ass['penalty']
                    
            
            
            assessment.append(ass_map)
            
        return render(request,
                      'messages.html',)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def process_procedure_summative_assessment_final_mark(request,pk,attempt_pk):
    '''
    Process the final mark
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 12:
        
        student_registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        learning_programme_cohort = student_registration.registration_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = student_registration.registration_period.period
        learning_programme_cohort_registration_period = student_registration.registration_period
          
        attempt_user = StudentProcedureSummativeAssessment.objects.get(id = attempt_pk)
            
        assessment = []
        
        total = 0
        total_marks = 0
        total_marks_percentage = 0

        all_questions_answered = True
        
        assessments = list(CohortRegistrationProcedureSummativeTaskAssessment.
                           objects.
                           filter(
                               task = attempt_user.attempt.cohort_procedure, 
                               task__cohort_registration_period = student_registration.registration_period,                           
                           ).values('question','id','question_type','number','penalty'))
        penalty = 0
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'question':ass['question'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number']}
            
            if ass['question_type'] == 'Question':
                total = total + 1
                           
                check_answer = (StudentProcedureSummativeAssessmentAnswer.
                                objects.
                                filter(
                                    attempt = attempt_user,
                                    assessment_id = ass['id']
                                ))
            
                if check_answer.exists():
                    answer = check_answer.first()
                
                    ass_map['answer_id'] = answer.id
                    ass_map['answer_answer'] = answer.answer
                    ass_map['answer_comment'] = answer.comment
                    
                    if ass_map['answer_answer'] == 'Competent':
                        total_marks = total_marks + 1
                        total_marks_percentage = round((total_marks/total)*100)
                    elif ass_map['answer_answer'] == 'Not Applicable':
                        total = total - 1
                    elif ass_map['answer_answer'] == 'Not Yet Competent':
                        
                        penalty = penalty + ass['penalty']

                else:
                    all_questions_answered = False
                    
            assessment.append(ass_map)
            
        total_marks_percentage_before_penalty = total_marks_percentage
        total_marks_percentage = total_marks_percentage  - penalty

        if all_questions_answered:
            attempt_user.assessor_mark = total_marks_percentage
            attempt_user.save()

            messages.success(request,"Final Mark Processed and Saved")
        else:
            messages.warning(request,"Marks not Processed, all questions need to be marked")
            
        if  request.user.logged_in_role_id == 12:
            return render(request,
                      'students/lecturer/period_registered_students_wil_procedure_summative_assessment.html',
                      { 'assessment':assessment,
                        'learning_programme_cohort':learning_programme_cohort,
                        'learning_programme':learning_programme,
                        'learning_programme_cohort_period':learning_programme_cohort_period,
                        'student_registration':student_registration,
                        'procedure_entry':attempt_user,
                        'total_marks':total_marks,
                        'total':total,
                        'learning_programme_cohort_registration_period':learning_programme_cohort_registration_period,
                        'total_marks_percentage':total_marks_percentage,
                        'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                        'penalty':penalty,
                       })
        else:
            return render(request,
                      'students/lecturer/period_registered_students_wil_procedure_summative_assessment.html',
                      { 'assessment':assessment,
                        'learning_programme_cohort':learning_programme_cohort,
                        'learning_programme':learning_programme,
                        'learning_programme_cohort_period':learning_programme_cohort_period,
                        'learning_programme_cohort_registration_period':learning_programme_cohort_registration_period,
                        'student_registration':student_registration,
                        'procedure_entry':attempt_user,
                        'total_marks':total_marks,
                        'total':total,
                        'total_marks_percentage':total_marks_percentage,
                        'total_marks_percentage_before_penalty':total_marks_percentage_before_penalty,
                        'penalty':penalty,
                       })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


'''
Facility HoD Views
'''

class FacilityWardStudents(LoginRequiredMixin,ListView):
    template_name = 'students/facility/wil_students_blocks.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 11:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(FacilityWardStudents, self).get(*args, **kwargs)

    def get_queryset(self):
        logsheet_entries = list(StudentLogSheet.objects.
                                filter(facility_ward_id = self.kwargs['pk']).
                                values('registration__student_learning_programme__student__first_name',
                                        'registration__student_learning_programme__student__last_name',
                                        'registration__student_learning_programme__student__student_number',
                                        'registration__student_learning_programme__student__email',
                                        'registration__student_learning_programme__student__cellphone',
                                        'competent',
                                        'registration_id',
                                        'date',
                                        'start',
                                        'end',
                                        'id',
                                        'mentor_acknowledgment'))
        return  logsheet_entries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hod'] = HealthCareFacilityHOD.objects.get(user_id=self.request.user.id)
        context['ward'] = HealthCareFacilityWard.objects.get(id = self.kwargs['pk'])
        
        context['ward_menu'] = '--active'
        context['ward_menu_open'] = 'side-menu__sub-open'
        return context


@login_required()
def facility_ward_students(request,pk):
    
    if request.user.logged_in_role_id == 11:
        
        hod = HealthCareFacilityHOD.objects.get(user_id=request.user.id)
        ward = HealthCareFacilityWard.objects.get(id = pk)
        logsheet_entries = list(StudentLogSheet.objects.
                                filter(facility_ward_id = pk).
                                values('registration__student_learning_programme__student__first_name',
                                        'registration__student_learning_programme__student__last_name',
                                        'registration__student_learning_programme__student__student_number',
                                        'registration__student_learning_programme__student__email',
                                        'registration__student_learning_programme__student__cellphone',
                                        'competent',
                                        'registration_id',
                                        'date',
                                        'start',
                                        'end',
                                        'id'))
        return render(request,'students/facility/wil_students_blocks.html',{'students':logsheet_entries,
                                                                            'ward':ward,
                                                                            'hod':hod,
                                                                            'ward_menu':'--active',
                                                                            'ward_menu_open':'--active',
                                                                            })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def facility_ward_students_competency(request,pk):
    
    if request.user.logged_in_role_id == 11:
        
        students = request.POST.getlist('students_selected[]')
        for s_id in students:
            student_log = StudentLogSheet.objects.get(id = s_id)
                            
            if 'mentor_acknowledgment' in request.POST:
                student_log.mentor_acknowledgment = request.POST['mentor_acknowledgment']
                
            if 'mentor_comment' in request.POST:
                student_log.mentor_comment = request.POST['mentor_comment']
                
            student_log.save()
            
        messages.success(request,'Successfully updated competency')        
               
        return redirect('students:facility_ward_students',pk=pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def fetch_students_ward_shifts(request,month):
    '''
    Fetch learner shifts in a specific month
    '''

    if request.user.logged_in_role_id == 11:
        facility_unit_manager = HealthCareFacilityHOD.objects.get(user = request.user)
        current_year = today.year
        student_shifts = list(StudentEducationPlan.
                          objects.
                          filter(
                              education_plan_section_week__start_of_week__startswith = f'{current_year}-{month}',
                              facility = facility_unit_manager.facility).
                          values('registration__student_learning_programme__student__first_name',
                                 'registration__student_learning_programme__student__last_name',
                                 'registration__student_learning_programme__student__email',
                                 'registration__student_learning_programme__student__cellphone',
                                 'education_plan_section_week__start_of_week',
                                 'education_plan_section_week__end_of_week',
                                 'time_period',
                                 'block__block_name',
                                 'discipline__discipline',
                                 'id').
                            order_by('education_plan_section_week__start_of_week'))
        
        print(len(student_shifts),f'{current_year}-{month}')
        
        months = [
                    {'month':'Jan','id':'01'},
                    {'month':'Feb','id':'02'},
                    {'month':'Mar','id':'03'},
                    {'month':'Apr','id':'04'},
                    {'month':'May','id':'05'},
                    {'month':'June','id':'06'},
                    {'month':'Jul','id':'07'},
                    {'month':'Aug','id':'08'},
                    {'month':'Sept','id':'09'},
                    {'month':'Oct','id':'10'},
                    {'month':'Nov','id':'11'},
                    {'month':'Dec','id':'12'},
                ]
        
        return render(request,'students/facility/wil_students_shifts.html',{'student_shifts':student_shifts,
                                                                            'facility_unit_manager':facility_unit_manager,
                                                                            'shifts_menu':'--active',
                                                                            'months':months,
                                                                            'selected_month':month})



    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def view_learners_shift_days(request,pk,month):
    
    '''
    days of the week
    '''
    
    if (request.user.logged_in_role_id == 11):

        plan = StudentEducationPlan.objects.get(id = pk) 
        registration = plan.registration
        #check if days exist , if not add them
        if plan.days.count() == 0:
            # Generate a list of days between start_date and end_date
            days_in_week = [(plan.education_plan_section_week.start_of_week + timedelta(days=i)) for i in range(7)]
            for day in days_in_week:
                StudentEducationPlanDay.objects.create(
                    education_plan_section_week = plan,
                    day = day,
                )
                
        
        
        return render(request,'students/facility/wil_students_shift_days.html',{
                                                                  'plan':plan,
                                                                  'registration':registration,
                                                                  'shifts_menu':'--active',
                                                                  'selected_month':month})       
            
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def edit_learners_shifts(request,pk,month):
    
    '''
    days of the week
    '''
    
    if (request.user.logged_in_role_id == 11):

        days = request.POST.getlist('days_selected[]')
        for day_pk in days:
            day = StudentEducationPlanDay.objects.get(id = day_pk) 
            if request.POST['duty_shift'] != '0':
                day.duty_shift = request.POST['duty_shift']
                
            day.save()
                
        messages.success(request,'Successfully edited Shifts')
        
        return redirect('students:view_learners_shift_days',pk=pk,month=month)
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def ajax_student_fetch_facility_discipline_wards(request,pk):
    start_date = request.GET.get('start_date', None)
    registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
    education_plan_check = StudentEducationPlan.objects.filter(registration = registration,
                                               education_plan_section_week__start_of_week__lte = start_date,
                                               education_plan_section_week__end_of_week__gte = start_date)
    
    if education_plan_check.exists():
        education_plan = education_plan_check.first()

        facility = education_plan.facility

        if facility:

            info = []
            if facility.wards.count() > 0:
                for x in facility.wards.all():
                    info.append({'id':x.id,'ward':x.ward.ward})
                    
                data = {
                    'valid':1,
                    'facility':facility.name,
                }
                data['info'] = info
            else:
                data = {
                    'valid':0,
                    'message':'No wards found',
                    'facility':facility.name,
                }  

        else:
            data = {
                'valid':3,
                'message':f"The selected date has a block code of: { education_plan.block.block_name } and doesn't have a HealthCare facility attached to it",              
            }
       
    else:
        data = {
                'valid':2,
                'message':'No wards'
            }

    return JsonResponse(data)