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

class CoAssessorLearningProgrammeCohortList(LoginRequiredMixin,ListView):
    template_name = 'college/coassessor/learning_programme_cohorts.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 12:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CoAssessorLearningProgrammeCohortList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCohort.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['periods'] = LearningProgrammePeriod.objects.filter(learning_programme_id = self.kwargs['pk'])
        context['cohort_menu'] = '--active'
        return context


class CoAssessorLearningProgrammeCohortRegistrationPeriodList(LoginRequiredMixin,ListView):
    template_name = 'college/coassessor/learning_programme_cohort_registration_period.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 12:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CoAssessorLearningProgrammeCohortRegistrationPeriodList, self).get(*args, **kwargs)

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



class CoAssessorLearningProgrammeCohortRegistrationPeriodProcedureList(LoginRequiredMixin,ListView):
    template_name = 'college/coassessor/procedures.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 12:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CoAssessorLearningProgrammeCohortRegistrationPeriodProcedureList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'],co_assessor=self.request.user)

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
    


class CoAssessorLearningProgrammeCohortRegistrationPeriodProcedureSummativeList(LoginRequiredMixin,ListView):
    template_name = 'college/coassessor/summative_procedures.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 12:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CoAssessorLearningProgrammeCohortRegistrationPeriodProcedureSummativeList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'],co_assessor=self.request.user)

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
    
