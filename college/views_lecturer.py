import datetime
import threading
from django.shortcuts import render, redirect,HttpResponse,Http404
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from accounts.forms import UserForm
from accounts.models import Role, User
from accounts.views import password_gen
from college.print_master_plan import MyPrintMasterPlan
from configurable.models import ClinicalProcedureThemeTask
from django_nursing.email_functions import send_email_general
from django_nursing.utility_functions import sunday_year_weeks
from students.models import StudentLearningProgrammeRegistration
from .models import *
from .forms import *
from decimal import Decimal


# Create your views here.

class LecturerLearningProgrammeCohortList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/learing_programme_cohorts.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCohort.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['periods'] = LearningProgrammePeriod.objects.filter(learning_programme_id = self.kwargs['pk'])
        context['cohort_menu'] = '--active'
        return context



class LecturerLearningProgrammeCohortRegistrationPeriodList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/learing_programme_cohort_registration_period.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCohortRegistrationPeriod.objects.filter(learning_programme_cohort_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = self.kwargs['pk'])
        context['learning_programme_cohort'] = learning_programme_cohort 
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['periods'] = LearningProgrammePeriod.objects.filter(learning_programme_id = learning_programme_cohort.learning_programme_id)
        context['cohort_menu'] = '--active'
        return context



class LecturerEducationPlanYearList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/education_plans.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerEducationPlanYearList, self).get(*args, **kwargs)

    def get_queryset(self):
        #check if plan exists
        
        return  EducationPlanYear.objects.filter(cohort_registration_period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        context['cohort_menu'] = '--active'
        context['period'] = period
        context['cohort'] = period.learning_programme_cohort
        context['learning_programme'] = period.learning_programme_cohort.learning_programme
        
        return context




class LecturerEducationPlanYearWeeksList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/education_plan_weeks.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerEducationPlanYearWeeksList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  EducationPlanYearSectionWeeks.objects.filter(education_plan_year_section__education_plan_year_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cohort_menu'] = '--active'
        plan = EducationPlanYear.objects.get(id = self.kwargs['pk'])
        period = plan.cohort_registration_period

        context['plan'] = plan
        context['period'] = period
        context['blocks'] = ProgarmmeBlock.objects.all()
        
        return context



class LecturerLearningProgrammeCohortRegistrationPeriodProcedureList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/procedures.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodProcedureList, self).get(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.logged_in_role_id == 5:
            return  CohortRegistrationProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'],clinical_facilitator=self.request.user)
        elif self.request.user.logged_in_role_id == 4:
            return  CohortRegistrationProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'],lecturer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['procedures'] = ClinicalProcedureThemeTask.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    


class LecturerLearningProgrammeCohortRegistrationPeriodProcedureSummativeList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/summative_procedures.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodProcedureSummativeList, self).get(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.logged_in_role_id == 5:
            return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'],clinical_facilitator=self.request.user)
        elif self.request.user.logged_in_role_id == 4:
            return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'],assessor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['procedures'] = ClinicalProcedureThemeTask.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    
      

class LecturerLearningProgrammeCohortRegistrationPeriodModuleList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodModuleList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModule.objects.filter(cohort_registration_period__id = self.kwargs['pk'],lecturer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context


class LecturerLearningProgrammeCohortRegistrationPeriodSummativeModuleList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/summative_modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodSummativeModuleList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModule.objects.filter(cohort_registration_period__id = self.kwargs['pk'],lecturer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    
class LecturerLearningProgrammeCohortRegistrationPeriodProcedureStaffCoAssessorList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/learing_programme_cohort_registration_procedures_formative_co_assessor.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodProcedureStaffCoAssessorList, self).get(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.logged_in_role_id == 5:
            return  CohortRegistrationProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'],clinical_facilitator=self.request.user)
        elif self.request.user.logged_in_role_id == 4:
            return  CohortRegistrationProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'],lecturer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme

        role = Role.objects.get(id = 4) 
        all_lecturers = role.user_set.all()
        lecturers = all_lecturers
        
        role = Role.objects.get(id = 5) 
        all_facilitators = role.user_set.all()
        facilitators = all_facilitators

        context['lecturers'] = lecturers.union(facilitators)
        
        role = Role.objects.get(id = 12) 
        external_staff = role.user_set.all()
        context['external_staff'] = external_staff

        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context


@login_required()
def assign_procedure_formative_assessment_co_assessor(request,pk):

    '''
    Assign 
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
        
        procedures = request.POST.getlist('procedures_selected[]')
        
        if request.POST['staff_type'] == 'internal':        
            co_assessor = request.POST['co_assessor']
        else:
            if request.POST['co_assessor_external'] != '0':
                co_assessor = request.POST['co_assessor_external']
            else:
                form = ExternalStaffForm(request.POST)
                if form.is_valid():
                    staff = form.save(commit = False)
                    if 'health_facility' in request.POST:
                        staff.health_facility_id = request.POST['health_facility']

                    staff.save()

                    role = Role.objects.get(id = 12)

                    #check if user exists otherwise add it

                    check_user = User.objects.filter(email=request.POST['email']) 

                    if check_user.exists():
                        user = check_user.first()
                    else:
                        user_form = UserForm(request.POST)
                        if user_form.is_valid():
                            password_change_date = datetime.datetime.now() - datetime.timedelta(days=43, hours=-5)
                            password = password_gen(14)

                            user = user_form.save(commit=False)
                            user.email = user.email.lower()
                            user.set_password(password)
                            user.is_superuser = 0
                            user.is_staff = 0
                            user.is_active = 1
                            user.password_change_date = password_change_date.date()
                            user.save()
                        else:
                            messages.warning(request,user_form.errors)

                    user.roles.add(role)
                    staff.user = user
                    staff.save()

                    co_assessor = user.id

                    messages.success(request,"Successfully added external staff details")
                else:
                    messages.warning(request,form.errors)
            
        for app_pk in procedures:
            procedure = CohortRegistrationProcedure.objects.get(id = app_pk)
            
            if co_assessor != procedure.lecturer_id:
                procedure.co_assessor_id = co_assessor
            
            procedure.save()

        messages.success(request,"Successfully assigned co-assessor to selected procedures")

        return redirect('college:lecturer_learning_programme_cohort_registration_procedures_formative_co_assessor',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



class LecturerLearningProgrammeCohortRegistrationPeriodProcedureSummativeStaffCoAssessorList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/learing_programme_cohort_registration_procedures_summative_co_assessor.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodProcedureSummativeStaffCoAssessorList, self).get(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.logged_in_role_id == 5:
            return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'],clinical_facilitator=self.request.user)
        elif self.request.user.logged_in_role_id == 4:
            return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'],assessor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme

        role = Role.objects.get(id = 4) 
        all_lecturers = role.user_set.all()
        lecturers = all_lecturers
        
        role = Role.objects.get(id = 5) 
        all_facilitators = role.user_set.all()
        facilitators = all_facilitators

        context['lecturers'] = lecturers.union(facilitators)
        
        role = Role.objects.get(id = 12) 
        external_staff = role.user_set.all()
        context['external_staff'] = external_staff

        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    

@login_required()
def assign_procedure_summative_assessment_co_assessor(request,pk):

    '''
    Assign 
    '''

    if request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
        
        procedures = request.POST.getlist('procedures_selected[]')
        
        if request.POST['staff_type'] == 'internal':        
            co_assessor = request.POST['co_assessor']
        else:
            if request.POST['co_assessor_external'] != '0':
                co_assessor = request.POST['co_assessor_external']
            else:
                form = ExternalStaffForm(request.POST)
                if form.is_valid():
                    staff = form.save(commit = False)
                    if 'health_facility' in request.POST:
                        staff.health_facility_id = request.POST['health_facility']

                    staff.save()

                    role = Role.objects.get(id = 12)

                    #check if user exists otherwise add it

                    check_user = User.objects.filter(email=request.POST['email']) 

                    if check_user.exists():
                        user = check_user.first()
                    else:
                        user_form = UserForm(request.POST)
                        if user_form.is_valid():
                            password_change_date = datetime.datetime.now() - datetime.timedelta(days=43, hours=-5)
                            password = password_gen(14)

                            user = user_form.save(commit=False)
                            user.email = user.email.lower()
                            user.set_password(password)
                            user.is_superuser = 0
                            user.is_staff = 0
                            user.is_active = 1
                            user.password_change_date = password_change_date.date()
                            user.save()
                        else:
                            messages.warning(request,user_form.errors)

                    user.roles.add(role)
                    staff.user = user
                    staff.save()

                    co_assessor = user.id

                    messages.success(request,"Successfully added external staff details")
                else:
                    messages.warning(request,form.errors)
            
        for app_pk in procedures:
            procedure = CohortRegistrationProcedureSummative.objects.get(id = app_pk)
            
            procedure.co_assessor_id = co_assessor
            
            procedure.save()

        messages.success(request,"Successfully assigned co-assessor to selected procedures")

        return redirect('college:lecturer_learning_programme_cohort_registration_procedures_summative_co_assessor',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class LecturerLearningProgrammeCohortRegistrationPeriodALLModulesList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/all_modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodALLModulesList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModule.objects.filter(cohort_registration_period__id = self.kwargs['pk'],lecturer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    

class LecturerLearningProgrammeCohortRegistrationPeriodModuleRegistersList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/module_registers.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodModuleRegistersList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModuleRegister.objects.filter(module_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registered_module = CohortRegistrationPeriodModule.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort_registration_period = registered_module.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        module = registered_module.module

        context['units'] = module.study_units.all()
        context['registered_module'] = registered_module
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    

@login_required()
def cohort_registration_module_register_add(request,pk):

    if request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 4:

        registered_module = CohortRegistrationPeriodModule.objects.get(id = pk)

        form = CohortRegistrationPeriodModuleRegisterForm(request.POST)
        if form.is_valid():
            register = form.save(commit = False)
            register.module = registered_module
            if 'unit' in request.POST:
                register.unit_id = request.POST['unit']
            register.user = request.user

            register.save()

            messages.success(request,"Successfully added Register")
        else:
            messages.warning(request,form.errors)

        return redirect('college:lecturer_module_rosters',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def cohort_registration_module_register_edit(request,pk,roster_pk):

    if request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 4:

        roster_instance = CohortRegistrationPeriodModuleRegister.objects.get(id = roster_pk)
        form = CohortRegistrationPeriodModuleRegisterForm(request.POST,instance = roster_instance)
        if form.is_valid():
            register = form.save(commit = False)
            if 'unit' in request.POST:
                register.unit_id = request.POST['unit']

            register.save()
            messages.success(request,"Successfully edited Register")
        else:
            messages.warning(request,form.errors)

        return redirect('college:lecturer_module_rosters',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def cohort_registration_module_register_delete(request,pk,roster_pk):

    if request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 4:

        try:
            roster_instance = CohortRegistrationPeriodModuleRegister.objects.get(id = roster_pk)
            roster_instance.delete()
            messages.success(request,"Successfully deleted Register")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:lecturer_module_rosters',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class LecturerLearningProgrammeCohortRegistrationPeriodModuleRegisterStudentsList(LoginRequiredMixin,ListView):
    template_name = 'college/lecturer/module_register_students.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 5 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LecturerLearningProgrammeCohortRegistrationPeriodModuleRegisterStudentsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModuleRegisterStudents.objects.filter(register_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        register = CohortRegistrationPeriodModuleRegister.objects.get(id = self.kwargs['pk'])
        registered_module = register.module
        learning_programme_cohort_registration_period = registered_module.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
      
        context['register'] = register
        context['registered_module'] = registered_module
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context


@login_required()
def cohort_registration_module_register_student_approve(request,pk,student_pk):

    if request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 4:
        
        student = CohortRegistrationPeriodModuleRegisterStudents.objects.get(id = student_pk)
        student.status = 'Approved'
        student.save()
        messages.success(request,"Approved")

        return redirect('college:lecturer_module_register_students',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def cohort_registration_module_register_student_reject(request,pk,student_pk):

    if request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 4:
        
        student = CohortRegistrationPeriodModuleRegisterStudents.objects.get(id = student_pk)
        student.status = 'Rejected'
        student.save()
        messages.success(request,"Rejected")

        return redirect('college:lecturer_module_register_students',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def cohort_registration_module_register_student_bulk_approve(request,pk):

    if request.user.logged_in_role_id == 5 or request.user.logged_in_role_id == 4:
        
        student_ids = request.POST.getlist('students_selected[]')
        
        for student_pk in student_ids:        
            student = CohortRegistrationPeriodModuleRegisterStudents.objects.get(id = student_pk)
            student.status = request.POST['status']
            student.save()
        
        messages.success(request,"Successfully edited attendance")

        return redirect('college:lecturer_module_register_students',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')