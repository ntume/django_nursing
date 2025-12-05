import datetime
import threading
from django.shortcuts import render, redirect,HttpResponse,Http404
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.http import JsonResponse
from accounts.forms import UserForm
from accounts.models import Role, User
from accounts.views import password_gen, reset_password_external
from college.print_master_plan import MyPrintMasterPlan
from configurable.models import ClinicalProcedureThemeTask
from django_nursing.email_functions import send_email_general
from django_nursing.utility_functions import sunday_year_weeks
from students.forms import StudentLearningProgrammeRegistrationRegisterForm
from students.models import StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationRegister
from .models import *
from .forms import *
from decimal import Decimal