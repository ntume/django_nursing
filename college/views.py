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
from college.print_master_plan_day import MyPrintMasterPlanWeek
from configurable.models import ClinicalProcedureThemeTask
from django_nursing.email_functions import send_email_activation_external, send_email_activation_staff, send_email_general
from django_nursing.utility_functions import sunday_year_weeks
from students.forms import StudentLearningProgrammeRegistrationRegisterForm
from students.models import StudentLearningProgrammeRegistration, StudentLearningProgrammeRegistrationRegister, StudentRegistrationModule
from .models import *
from .forms import *
from decimal import Decimal


# Create your views here.

class CollegeCampusList(LoginRequiredMixin,ListView):
    template_name = 'college/college_campus.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CollegeCampusList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CollegeCampus.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campus_menu'] = '--active'
        
        return context

@login_required()
def college_campus_add(request):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = CollegeCampusForm(request.POST)
        if form.is_valid():
            campus = form.save(commit = False)
            if 'physical_address_3' in request.POST:
                campus.physical_address_3 = request.POST['physical_address_3']
            if 'postal_code' in request.POST:
                campus.postal_code_id = request.POST['postal_code']

            campus.save()

            messages.success(request,"Successfully added campus details")
        else:
            messages.warning(request,form.errors)

        return redirect('college:college_campuses')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def college_campus_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        campus_instance = CollegeCampus.objects.get(id = pk)
        form = CollegeCampusForm(request.POST,instance = campus_instance)
        if form.is_valid():
            campus = form.save(commit = False)
            if 'physical_address_3' in request.POST:
                campus.physical_address_3 = request.POST['physical_address_3']
            if 'postal_code' in request.POST:
                campus.postal_code_id = request.POST['postal_code']

            campus.save()
            messages.success(request,"Successfully edited college campus")
        else:
            messages.warning(request,form.errors)

        return redirect('college:college_campuses')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def college_campus_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            campus_instance = CollegeCampus.objects.get(id = pk)
            campus_instance.delete()
            messages.success(request,"Successfully deleted college campus")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:college_campuses')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')




class HealthcareFacilitiesList(LoginRequiredMixin,ListView):
    template_name = 'college/health_care_facilities.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(HealthcareFacilitiesList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  HealthCareFacility.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['health_care_facility_menu'] = '--active'
        context['learning_programmes'] = LearningProgramme.objects.all()
        context['disciplines'] = Discipline.objects.all()
        context['ward_list'] = Ward.objects.all()
        return context

@login_required()
def health_care_facility_add(request):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        form = HealthCareFacilityForm(request.POST)
        if form.is_valid():
            hc = form.save(commit = False)
            if 'physical_address_3' in request.POST:
                hc.physical_address_3 = request.POST['physical_address_3']
            if 'postal_code' in request.POST:
                hc.postal_code_id = request.POST['postal_code']

            hc.save()

            messages.success(request,"Successfully added healthcare facility details")
        else:
            messages.warning(request,form.errors)

        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def health_care_facility_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        hc_instance = HealthCareFacility.objects.get(id = pk)
        form = HealthCareFacilityForm(request.POST,instance = hc_instance)
        if form.is_valid():
            hc = form.save(commit = False)
            if 'physical_address_3' in request.POST:
                hc.physical_address_3 = request.POST['physical_address_3']
            if 'postal_code' in request.POST:
                hc.postal_code_id = request.POST['postal_code']

            hc.save()
            messages.success(request,"Successfully edited healthcare facility")
        else:
            messages.warning(request,form.errors)

        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def health_care_facility_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            hc_instance = HealthCareFacility.objects.get(id = pk)
            hc_instance.delete()
            messages.success(request,"Successfully deleted  healthcare facility")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def health_care_facility_learning_programme_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if learning programme exists

        check_lp = HealthCareFacilityLearningProgrammeNumbers.objects.filter(learning_programme_id = request.POST['learning_programme'],
                                                                             health_care_facility_id = pk).exists()
        if check_lp:
            messages.warning(request,'This programme exists for this facility. If you want to edit the numbers, click the edit button')
        else:
            form = HealthCareFacilityLearningProgrammeNumbersForm(request.POST)
            if form.is_valid():
                student_numbers = form.save(commit=False)
                student_numbers.learning_programme_id = request.POST['learning_programme']
                student_numbers.health_care_facility_id = pk
                student_numbers.save()
                messages.success(request,'Successfully added student capacity numbers')
            else:
                messages.warning(request,form.errors)
                
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def health_care_facility_learning_programme_edit(request,pk,lp_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if learning programme exists

        lp_instance = HealthCareFacilityLearningProgrammeNumbers.objects.get(id = lp_pk)
       
        form = HealthCareFacilityLearningProgrammeNumbersForm(request.POST,instance=lp_instance)
        if form.is_valid():
            form.save()
            messages.success(request,'Successfully edited student capacity numbers')
        else:
            messages.warning(request,form.errors)
                
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def health_care_facility_learning_programme_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if learning programme exists

        lp_instance = HealthCareFacilityLearningProgrammeNumbers.objects.get(id = pk)
       
        try:
            lp_instance.delete()
            messages.success(request,"Successfully deleted  healthcare facility learning programme")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")
                
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def health_care_facility_discipline_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if discipline exists

        check_lp = HealthCareFacilityDisciplineNumber.objects.filter(discipline_id = request.POST['discipline'],
                                                                     learning_programme_id = request.POST['learning_programme'],
                                                                     health_care_facility_id = pk).exists()
        if check_lp:
            messages.warning(request,'This discipline exists for this facility. If you want to edit the numbers, click the edit button')
        else:
            form = HealthCareFacilityDisciplineNumberForm(request.POST)
            if form.is_valid():
                student_numbers = form.save(commit=False)
                if 'discipline' in request.POST:
                    student_numbers.discipline_id = request.POST['discipline']
                if 'learning_programme' in request.POST:
                    student_numbers.learning_programme_id = request.POST['learning_programme']

                student_numbers.health_care_facility_id = pk
                student_numbers.save()
                messages.success(request,'Successfully added discipline student capacity numbers')
            else:
                messages.warning(request,form.errors)
                
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def health_care_facility_discipline_edit(request,pk,lp_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if learning programme exists

        lp_instance = HealthCareFacilityDisciplineNumber.objects.get(id = lp_pk)
       
        form = HealthCareFacilityDisciplineNumberForm(request.POST,instance=lp_instance)
        if form.is_valid():
            student_numbers = form.save(commit=False)
            
            student_numbers.save()
            messages.success(request,'Successfully edited student capacity numbers')
        else:
            messages.warning(request,form.errors)
                
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def health_care_facility_discipline_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        

        lp_instance = HealthCareFacilityDisciplineNumber.objects.get(id = pk)
       
        try:
            lp_instance.delete()
            messages.success(request,"Successfully deleted  healthcare facility discipline")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")
                
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    

@login_required()
def health_care_facility_wards_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        wards = request.POST.getlist('wards[]')
        for s_id in wards:
            ward = Ward.objects.get(id = s_id)
            #check if ward exists
            check_ward = HealthCareFacilityWard.objects.filter(ward_id = s_id,facility_id=pk).exists()
            if not check_ward:
                HealthCareFacilityWard.objects.create(ward_id = s_id,facility_id=pk)
               
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def health_care_facility_ward_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        

        lp_instance = HealthCareFacilityWard.objects.get(id = pk)
       
        try:
            lp_instance.delete()
            messages.success(request,"Successfully deleted  healthcare facility ward")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")
                
        return redirect('college:health_care_facilities')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



class HealthcareFacilityHODList(LoginRequiredMixin,ListView):
    template_name = 'college/health_care_facility_hods.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(HealthcareFacilityHODList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  HealthCareFacilityHOD.objects.filter(facility_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['health_care_facility_menu'] = '--active'
        context['health_care_facility'] = HealthCareFacility.objects.get(id=self.kwargs['pk'])
     
        context['races'] = Race.objects.all()
        context['genders'] = Gender.objects.all()
        context['titles'] = ['Mr',
                             'Mrs',
                             'Ms',
                             'Dr',
                             'Adv',
                             'Hon',
                             'Prof']
        return context

@login_required()
def health_care_facility_hod_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        form = HealthCareFacilityHODForm(request.POST)
        if form.is_valid():
            hc = form.save(commit = False)
            hc.facility_id = pk
            if 'gender' in request.POST:
                hc.gender_id = request.POST['gender']
            if 'race' in request.POST:
                hc.race_id = request.POST['race']

            hc.save()
            
            role = Role.objects.get(id = 11)

            #check if user exists otherwise add it

            check_user = User.objects.filter(email=request.POST['email']) 

            if check_user.exists():
                user = check_user.first()
                password = 'Your original Password'
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
            hc.user = user
            hc.save()
            
            try:    
                response = send_email_activation_staff(user.email,user.first_name,password) 
            except Exception as e:
                print(str(e),password)

            messages.success(request,"Successfully added healthcare facility HOD")
        else:
            messages.warning(request,form.errors)

        return redirect('college:health_care_facility_hods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def health_care_facility_hod_edit(request,pk,hod_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        hc_instance = HealthCareFacilityHOD.objects.get(id = hod_pk)
        form = HealthCareFacilityHODForm(request.POST,instance = hc_instance)
        if form.is_valid():
            hc = form.save(commit = False)
            if 'gender' in request.POST:
                hc.gender_id = request.POST['gender']
            if 'race' in request.POST:
                hc.race_id = request.POST['race']

            hc.save()
            
            if hc.user:
                user = hc.user
                user.first_name = hc.first_name
                user.last_name = hc.last_name
                user.save()
                
            messages.success(request,"Successfully edited healthcare facility hod")
        else:
            messages.warning(request,form.errors)

        return redirect('college:health_care_facility_hods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def health_care_facility_hod_delete(request,pk,hod_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            hc_instance = HealthCareFacilityHOD.objects.get(id = hod_pk)
            hc_instance.delete()
            messages.success(request,"Successfully deleted  healthcare facility HOD")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:health_care_facility_hods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def health_care_facility_hod_reset_password(request,pk,hod_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        hc_instance = HealthCareFacilityHOD.objects.get(id = hod_pk)
        reset_password_external(hc_instance.user)
        
        return redirect('college:health_care_facility_hods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def health_care_facility_hod_ward_add(request,pk,hod_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        hc_instance = HealthCareFacilityHOD.objects.get(id = hod_pk)
        wards = request.POST.getlist('wards[]')
        for s_id in wards:
            ward = HealthCareFacilityWard.objects.get(id = s_id)
            hc_instance.wards.add(ward)
        
        return redirect('college:health_care_facility_hods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def health_care_facility_hod_ward_remove(request,pk,hod_pk,ward_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        hc_instance = HealthCareFacilityHOD.objects.get(id = hod_pk)
        ward = HealthCareFacilityWard.objects.get(id = ward_pk)
        hc_instance.wards.remove(ward)
        
        return redirect('college:health_care_facility_hods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



class ModeratorsList(LoginRequiredMixin,ListView):
    template_name = 'college/moderators_list.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ModeratorsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Moderator.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['moderator_menu'] = '--active'
     
        context['races'] = Race.objects.all()
        context['genders'] = Gender.objects.all()
        context['titles'] = ['Mr',
                             'Mrs',
                             'Ms',
                             'Dr',
                             'Adv',
                             'Hon',
                             'Prof']
        return context

@login_required()
def moderator_add(request):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        form = ModeratorForm(request.POST)
        if form.is_valid():
            hc = form.save(commit = False)            
            if 'gender' in request.POST:
                hc.gender_id = request.POST['gender']
            if 'race' in request.POST:
                hc.race_id = request.POST['race']

            hc.save()
            
            role = Role.objects.get(id = 7)

            #check if user exists otherwise add it

            check_user = User.objects.filter(email=request.POST['email']) 

            if check_user.exists():
                user = check_user.first()
                password = 'Your original password'
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
            hc.user = user
            hc.save()
            
            try:    
                response = send_email_activation_staff(user.email,user.first_name,password) 
            except Exception as e:
                print(str(e),password)

            messages.success(request,"Successfully added Moderator")
        else:
            messages.warning(request,form.errors)

        return redirect('college:moderators')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def moderator_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        hc_instance = Moderator.objects.get(id = pk)
        form = ModeratorForm(request.POST,instance = hc_instance)
        if form.is_valid():
            hc = form.save(commit = False)
            if 'gender' in request.POST:
                hc.gender_id = request.POST['gender']
            if 'race' in request.POST:
                hc.race_id = request.POST['race']

            hc.save()
            
            if hc.user:
                user = hc.user
                user.first_name = hc.first_name
                user.last_name = hc.last_name
                user.save()
                
            messages.success(request,"Successfully edited Moderator")
        else:
            messages.warning(request,form.errors)

        return redirect('college:moderators')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def moderator_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            hc_instance = Moderator.objects.get(id = pk)
            hc_instance.delete()
            messages.success(request,"Successfully deleted Moderator")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:moderators')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def moderator_reset_password(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        hc_instance = Moderator.objects.get(id = pk)
        reset_password_external(hc_instance.user)
        
        return redirect('college:moderators')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')




class StaffList(LoginRequiredMixin,ListView):
    template_name = 'college/staff.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(StaffList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Staff.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff_menu'] = '--active'
        context['races'] = Race.objects.all()
        context['roles'] = Role.objects.all()
        context['genders'] = Gender.objects.all()
        context['campuses'] = CollegeCampus.objects.all()
        context['titles'] = ['Mr',
                             'Mrs',
                             'Ms',
                             'Dr',
                             'Adv',
                             'Hon',
                             'Prof']
        return context

@login_required()
def staff_add(request):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit = False)
            if 'gender' in request.POST:
                staff.gender_id = request.POST['gender']
            if 'race' in request.POST:
                staff.race_id = request.POST['race']
            if 'college_campus' in request.POST:
                staff.college_campus_id = request.POST['college_campus']

            staff.save()

            role = Role.objects.get(id = request.POST['role'])

            #check if user exists otherwise add it

            check_user = User.objects.filter(email=request.POST['email']) 

            if check_user.exists():
                user = check_user.first()
                password = 'Your original Password'
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
            
            try:    
                response = send_email_activation_staff(user.email,user.first_name,password) 
            except Exception as e:
                print(str(e),password)

            messages.success(request,"Successfully added staff details")
        else:
            messages.warning(request,form.errors)

        return redirect('college:staff_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def staff_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        staff_instance = Staff.objects.get(id = pk)
        form = StaffForm(request.POST,instance = staff_instance)
        if form.is_valid():
            staff = form.save(commit = False)
            if 'gender' in request.POST:
                staff.gender_id = request.POST['gender']
            if 'race' in request.POST:
                staff.race_id = request.POST['race']
            if 'college_campus' in request.POST:
                staff.college_campus_id = request.POST['college_campus']

            staff.save()
            if staff.user:
                user = staff.user
                user.first_name = staff.first_name
                user.last_name = staff.last_name
                user.save()

            messages.success(request,"Successfully edited college staff")
        else:
            messages.warning(request,form.errors)

        return redirect('college:staff_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def staff_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            staff_instance = Staff.objects.get(id = pk)
            staff_instance.active = 'No'
            staff_instance.save()
            messages.success(request,"Successfully deactivated college staff")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:staff_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def add_staff_role(request,pk):
    '''
    Add roles to user
    '''
    staff_instance = Staff.objects.get(id=pk)
    user = staff_instance.user
    role = Role.objects.get(id = request.POST['role'])
    user.roles.add(role)
    messages.success(request,'Successfully added role to user')

    return redirect('college:staff_list')



@login_required()
def remove_staff_role(request,pk,role_pk):
    '''
    remove roles to user
    '''
    staff_instance = Staff.objects.get(id=pk)
    user = staff_instance.user
    role = Role.objects.get(id = role_pk)
    user.roles.remove(role)
    messages.success(request,'Successfully removed role from user')

    return redirect('college:staff_list')




class RegistrationPeriodList(LoginRequiredMixin,ListView):
    template_name = 'college/registration_periods.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(RegistrationPeriodList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  RegistrationPeriod.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration_period_menu_open'] = '--active'
        context['blocks'] = RegistrationBlockCode.objects.all()
        context['learning_programme_periods'] = LearningProgrammePeriod.objects.all()
        return context

@login_required()
def registration_period_add(request):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = RegistrationPeriodForm(request.POST)
        if form.is_valid():
            reg = form.save(commit = False)
            if 'block' in request.POST:
                reg.block_id = request.POST['block']   
                
            reg.save()                    

            messages.success(request,"Successfully added Registration period details")
        else:
            messages.warning(request,form.errors)

        return redirect('college:registration_period_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def registration_period_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        block_instance = RegistrationPeriod.objects.get(id = pk)
        form = RegistrationPeriodForm(request.POST,instance = block_instance)
        if form.is_valid():
            reg = form.save(commit = False)
            if 'block' in request.POST:
                reg.block_id = request.POST['block']   
                
            reg.save() 
            
            messages.success(request,"Successfully edited Registration Period")
        else:
            messages.warning(request,form.errors)

        return redirect('college:registration_period_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def registration_period_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            i_instance = RegistrationPeriod.objects.get(id = pk)
            i_instance.delete()
            messages.success(request,"Successfully deleted Registration Period")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:registration_period_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def registration_period_learning_programme_period_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        registration_period = RegistrationPeriod.objects.get(id = pk)
        lp_periods = request.POST.getlist('learning_programme_periods[]')
        for m_id in lp_periods:        
            check_programme_exists = LearningProgrammePeriodRegistration.objects.filter(learning_programme_period_id = m_id,
                                                                                        registration_period = registration_period).exists()
            if not check_programme_exists:
                lp_registration = LearningProgrammePeriodRegistration.objects.create(learning_programme_period_id = m_id,
                                                                   registration_period = registration_period)
                
                #add the modules
                lp_period = LearningProgrammePeriod.objects.get(id = m_id)
                
                for module in lp_period.modules.all():
                    m = LearningProgrammePeriodRegistrationModule.objects.create(
                        learning_programme_period_registration_period = lp_registration,
                        module = module.module,
                        entrance_year_mark = module.module.entrance_year_mark,
                        summative_weight = module.module.summative_weight,
                        assignment_weight = module.module.assignment_weight,
                        test_weight = module.module.test_weight,
                    )
                              
                    #next add the formative assessments
                    for assessment in module.module.formative.all():
                        a = LPRegistrationPeriodModuleFormative.objects.create(
                            module = m,
                            assessment_type = assessment.assessment_type,
                            title = assessment.title,
                            weight = assessment.weight,
                        )
                
                
                
                           
        messages.success(request,"Successfully added Learning Programme Periods")
        
        return redirect('college:registration_period_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        
        
@login_required() 
def registration_period_learning_programme_period_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
                
        try:
            i_instance = LearningProgrammePeriodRegistration.objects.get(id = pk)
            i_instance.delete()
            messages.success(request,"Successfully deleted Learning Programme Period")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:registration_period_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
    
class LearningProgrammeRegistrationModulesList(LoginRequiredMixin,ListView):
    template_name = 'college/registration_period_modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeRegistrationModulesList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodRegistrationModule.objects.filter(learning_programme_period_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_registration_period = LearningProgrammePeriodRegistration.objects.get(id = self.kwargs['pk'])
        learning_programme_period = learning_programme_registration_period.learning_programme_period
         
        context['learning_programme_period'] = learning_programme_period
        context['learning_programme'] = learning_programme_period.learning_programme
        context['modules'] = learning_programme_period.learning_programme.modules.all()
        context['registration_period_menu_open'] = '--active'
        context['learning_programme_registration_period'] = learning_programme_registration_period
        return context

@login_required()
def learning_programme_registration_modules_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        #check if cohort ihas period
        
        modules = request.POST.getlist('modules[]')
        for p_id in modules:
            module = LearningProgrammeModule.objects.get(id = p_id)
            check_p = LearningProgrammePeriodRegistrationModule.objects.filter(module__id = p_id,cohort_registration_period__id = pk).exists()

            if check_p:
                messages.warning(request,'Module added previously')
            else:
                added_module = LearningProgrammePeriodRegistrationModule.objects.create(
                    module_id = p_id,
                    learning_programme_period_registration_period_id = pk,     
                    entrance_year_mark = module.entrance_year_mark,
                    summative_weight = module.summative_weight,
                    assignment_weight = module.assignment_weight,
                    test_weight = module.test_weight               
                )
                
                LPRegistrationPeriodModuleFormative.objects.filter(module = added_module).delete()
                    
                for assessment in module.formative.all():
                    #remove all assessments for that module and copy over the template
                    LPRegistrationPeriodModuleFormative.objects.create(
                        module = added_module,
                        assessment_type = assessment.assessment_type,
                        title = assessment.title,
                        weight = assessment.weight                        
                    )

        messages.success(request,"Successfully added module")
            
        return redirect('college:learning_programme_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_registration_modules_edit(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        module = LearningProgrammePeriodRegistrationModule.objects.get(id = module_pk)
        form = LearningProgrammePeriodRegistrationModuleForm(request.POST,instance = module)
        if form.is_valid():
            module = form.save(commit=False)
            module.save()

            messages.success(request,"Successfully edited module")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_registration_modules_delete(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            module = LearningProgrammePeriodRegistrationModule.objects.get(id = module_pk)
            module.delete()
            messages.success(request,"Successfully removed Module")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

class BackgroundThreadCopyRegistrationModuleAssessments(threading.Thread):
    
    def __init__(self,request,learning_programme_registration_period):
        self.learning_programme_registration_period = learning_programme_registration_period 
        self.request = request

        threading.Thread.__init__(self)

    def run(self):
        for module in self.learning_programme_registration_period.modules.all():
            #check if module has an assessment
            if module.module.formative.count() > 0:
                LPRegistrationPeriodModuleFormative.objects.filter(module = module).delete()
                    
                for assessment in module.module.formative.all():
                    #remove all assessments for that module and copy over the template
                    LPRegistrationPeriodModuleFormative.objects.create(
                        module = module,
                        assessment_type = assessment.assessment_type,
                        title = assessment.title,
                        weight = assessment.weight                        
                    )
        email_body = 'Assessments have been copied over'
        title = 'Module Assessments Copied'
        name = self.request.user.first_name
        to = self.request.user.email
        send_email_general(to,name,title,email_body)

@login_required()
def copy_registration_modules_assessments(request,pk):
    '''
    copy all the module assessments
    '''
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        learning_programme_registration_period = LearningProgrammePeriodRegistrationModule.objects.get(id = pk)
        
        BackgroundThreadCopyRegistrationModuleAssessments(request,learning_programme_registration_period).start()
        
        messages.success(request,'The assessments will be copied over and an email will be sent to you once done')
     
        return redirect('college:learning_programme_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
       

@login_required()
def learning_programme_registration_module_formative_add(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LPRegistrationPeriodModuleFormativeForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.module_id = module_pk
            assessment.save()

            messages.success(request,"Successfully added Assessment")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_registration_module_formative_edit(request,pk,module_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        assessment = LPRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
        form = LPRegistrationPeriodModuleFormativeForm(request.POST,instance = assessment)
        if form.is_valid():
            form.save()

            messages.success(request,"Successfully edited Assessment ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_registration_module_formative_delete(request,pk,module_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            assessment = LPRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
            assessment.delete()
            messages.success(request,"Successfully deleted Assessment")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

    
    
    
    
    
    
    
    


class LearningProgrammeList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programmes.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgramme.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_add(request):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request,"Successfully added learning programme")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programmes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        lp = LearningProgramme.objects.get(id = pk)
        form = LearningProgrammeForm(request.POST,instance = lp)
        if form.is_valid():
            form.save()
            messages.success(request,"Successfully edited Learning Programme")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programmes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_toggle(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        lp = LearningProgramme.objects.get(id = pk)
        if lp.active == 'No':            
            lp.active = 'Yes'
            messages.success(request,"Successfully activated learning programme")
        else:
            lp.active = 'No'
            messages.success(request,"Successfully deactivated learning programme")

        lp.save()
        return redirect('college:learning_programmes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def learning_programme_period_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammePeriodForm(request.POST)
        if form.is_valid():
            period = form.save(commit=False)
            period.learning_programme_id = pk
            period.save()
            messages.success(request,"Successfully added Learning Programme Period")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programmes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_period_edit(request,pk,period_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        period = LearningProgrammePeriod.objects.get(id = period_pk)
        form = LearningProgrammePeriodForm(request.POST,instance=period)
        if form.is_valid():
            period = form.save(commit=False)
            period.learning_programme_id = pk
            period.save()
            messages.success(request,"Successfully edited Learning Programme Period")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programmes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_period_delete(request,pk,period_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            period = LearningProgrammePeriod.objects.get(id = period_pk)
            period.delete()
            messages.success(request,"Successfully deleted learning programme period")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programmes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')




class LearningProgrammePeriodWilRequirementsList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_period_requirements.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammePeriodWilRequirementsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodWILRequirement.objects.filter(period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammePeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = period.learning_programme
        context['period'] = period
        context['disciplines'] = Discipline.objects.all()
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_period_wil_requirement_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        #check if the discipline exists
        
        check_pline_exists = LearningProgrammePeriodWILRequirement.objects.filter(period_id = pk,
                                                                                  discipline_id = request.POST['discipline']).exists()

        if check_pline_exists:
            messages.warning(request,'Sorry this discipline exists')
        else:
            form = LearningProgrammePeriodWILRequirementForm(request.POST,request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.period_id = pk
                doc.discipline_id = request.POST['discipline']
                doc.save()
                messages.success(request,"Successfully added WIL Requirement")
            else:
                messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_wil_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_period_wil_requirement_edit(request,pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammePeriodWILRequirement.objects.get(id = wil_pk)
        form = LearningProgrammePeriodWILRequirementForm(request.POST,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()

            messages.success(request,"Successfully edited WIL Requirement")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_wil_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_period_wil_requirement_delete(request,pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammePeriodWILRequirement.objects.get(id = wil_pk)
            lp.delete()
            messages.success(request,"Successfully deleted WIL Requirement")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_period_wil_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class LearningProgrammePeriodModuleList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_period_modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammePeriodModuleList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodModule.objects.filter(period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammePeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = period.learning_programme
        context['period'] = period
        context['modules'] = LearningProgrammeModule.objects.filter(learning_programme = period.learning_programme)
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_period_module_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        #check if the discipline exists
        
        modules = request.POST.getlist('modules[]')
        for m_id in modules:        
            check_module_exists = LearningProgrammePeriodModule.objects.filter(period_id = pk,
                                                                              module_id = m_id).exists()
            

            if check_module_exists:
                messages.warning(request,'Sorry this module exists')
            else:
                LearningProgrammePeriodModule.objects.create(period_id = pk,module_id = m_id)
                messages.success(request,"Successfully added module")
            
        return redirect('college:learning_programme_period_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_period_module_delete(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammePeriodModule.objects.get(id = module_pk)
            lp.delete()
            messages.success(request,"Successfully deleted Module from period")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_period_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    




class LearningProgrammePeriodWilRequirementsList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_period_requirements.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammePeriodWilRequirementsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodWILRequirement.objects.filter(period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammePeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = period.learning_programme
        context['period'] = period
        context['disciplines'] = Discipline.objects.all()
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_period_wil_requirement_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        #check if the discipline exists
        
        check_pline_exists = LearningProgrammePeriodWILRequirement.objects.filter(period_id = pk,
                                                                                  discipline_id = request.POST['discipline']).exists()

        if check_pline_exists:
            messages.wafrning(request,'Sorry this discipline exists')
        else:
            form = LearningProgrammePeriodWILRequirementForm(request.POST,request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.period_id = pk
                doc.discipline_id = request.POST['discipline']
                doc.save()
                messages.success(request,"Successfully added WIL Requirement")
            else:
                messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_wil_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_period_wil_requirement_edit(request,pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammePeriodWILRequirement.objects.get(id = wil_pk)
        form = LearningProgrammePeriodWILRequirementForm(request.POST,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()

            messages.success(request,"Successfully edited WIL Requirement")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_wil_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_period_wil_requirement_delete(request,pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammePeriodWILRequirement.objects.get(id = wil_pk)
            lp.delete()
            messages.success(request,"Successfully deleted WIL Requirement")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_period_wil_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class LearningProgrammePeriodBlockRequirementsList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_period_block_requirements.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammePeriodBlockRequirementsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodWILBlockHours.objects.filter(period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammePeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = period.learning_programme
        context['period'] = period
        context['blocks'] = ProgarmmeBlock.objects.all()
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_period_wil_block_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        #check if the discipline exists
        
        check_pline_exists = LearningProgrammePeriodWILBlockHours.objects.filter(period_id = pk,
                                                                                  block_id = request.POST['block']).exists()

        if check_pline_exists:
            messages.warning(request,'Sorry this block exists')
        else:
            form = LearningProgrammePeriodWILBlockHoursForm(request.POST,request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.period_id = pk
                doc.block_id = request.POST['block']
                doc.save()
                messages.success(request,"Successfully added Block Hours")
            else:
                messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_block_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_period_wil_block_edit(request,pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammePeriodWILBlockHours.objects.get(id = wil_pk)
        form = LearningProgrammePeriodWILBlockHoursForm(request.POST,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()

            messages.success(request,"Successfully edited  Block Hours")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_block_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_period_wil_block_delete(request,pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammePeriodWILBlockHours.objects.get(id = wil_pk)
            lp.delete()
            messages.success(request,"Successfully deleted Block Hours")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_period_block_requirements',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



class LearningProgrammePeriodSessionList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_period_sessions.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammePeriodSessionList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodTimeTableSession.objects.filter(learning_programme_period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammePeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = period.learning_programme
        context['period'] = period
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_period_session_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        #check if the discipline exists
        
        
        form = LearningProgrammePeriodTimeTableSessionForm(request.POST,request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.learning_programme_period_id = pk
            doc.created_by = request.user
            doc.save()
            messages.success(request,"Successfully added Timetable Session")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_sessions',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_period_session_edit(request,pk,session_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammePeriodTimeTableSession.objects.get(id = session_pk)
        form = LearningProgrammePeriodTimeTableSessionForm(request.POST,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()

            messages.success(request,"Successfully edited Session")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_sessions',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_period_session_delete(request,pk,session_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammePeriodTimeTableSession.objects.get(id = session_pk)
            lp.delete()
            messages.success(request,"Successfully deleted Session")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_period_sessions',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class LearningProgrammePeriodModeratorCriteriaReportList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_period_moderator_criteria_report.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammePeriodModeratorCriteriaReportList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodModerationCriteria.objects.filter(learning_programme_period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammePeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = period.learning_programme
        context['period'] = period
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_period_moderator_criteria_report_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        #check if the discipline exists
        
        
        form = LearningProgrammePeriodModerationCriteriaForm(request.POST,request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.learning_programme_period_id = pk
            doc.role_id = request.POST['role']
            doc.created_by = request.user
            doc.save()
            messages.success(request,"Successfully added Moderation Criteria")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_moderation_criteria',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_period_moderator_criteria_report_edit(request,pk,criteria_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammePeriodModerationCriteria.objects.get(id = criteria_pk)
        form = LearningProgrammePeriodModerationCriteriaForm(request.POST,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.role_id = request.POST['role']
            doc.save()

            messages.success(request,"Successfully edited Moderation Criteria")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_moderation_criteria',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_period_moderator_criteria_report_delete(request,pk,criteria_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammePeriodModerationCriteria.objects.get(id = criteria_pk)
            lp.delete()
            messages.success(request,"Successfully deleted Criteria")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_period_moderation_criteria',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class LearningProgrammePeriodModeratorCriteriaWILReportList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_period_moderator_criteria_wil_report.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammePeriodModeratorCriteriaWILReportList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammePeriodModerationCriteriaWIL.objects.filter(learning_programme_period_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammePeriod.objects.get(id = self.kwargs['pk'])
        context['learning_programme'] = period.learning_programme
        context['period'] = period
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_period_moderator_criteria_wil_report_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        #check if the discipline exists
        
        
        form = LearningProgrammePeriodModerationCriteriaWILForm(request.POST,request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.learning_programme_period_id = pk
            doc.role_id = request.POST['role']
            doc.created_by = request.user
            doc.save()
            messages.success(request,"Successfully added Moderation Criteria for WIL")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_moderation_criteria_wil',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_period_moderator_criteria_wil_report_edit(request,pk,criteria_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammePeriodModerationCriteriaWIL.objects.get(id = criteria_pk)
        form = LearningProgrammePeriodModerationCriteriaWILForm(request.POST,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.role_id = request.POST['role']
            doc.save()

            messages.success(request,"Successfully edited Moderation Criteria for WIL")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_period_moderation_criteria_wil',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_period_moderator_criteria_wil_report_delete(request,pk,criteria_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammePeriodModerationCriteriaWIL.objects.get(id = criteria_pk)
            lp.delete()
            messages.success(request,"Successfully deleted Criteria")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_period_moderation_criteria_wil',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



class LearningProgrammeDocumentList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_documents.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeDocumentList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeDocument.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_document_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeDocumentForm(request.POST,request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.learning_programme_id = pk
            doc.save()

            if 'document' in request.FILES:
                form_file = LearningProgrammeDocumentFileForm(request.POST,request.FILES,instance=doc)
                if form_file.is_valid():
                    form_file.save()

            messages.success(request,"Successfully added learning programme document")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_documents',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_document_edit(request,pk,doc_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammeDocument.objects.get(id = doc_pk)
        form = LearningProgrammeDocumentForm(request.POST,request.FILES,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.learning_programme_id = pk
            doc.save()

            if 'document' in request.FILES:
                form_file = LearningProgrammeDocumentFileForm(request.POST,request.FILES,instance=doc)
                if form_file.is_valid():
                    form_file.save()

            messages.success(request,"Successfully edited Learning Programme Document")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_documents',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def toggle_learning_programme_document(request,pk,doc_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        doc = LearningProgrammeDocument.objects.get(id = doc_pk)
        if doc.active == 'Yes':
            doc.active = 'No'
        else:
            doc.active='Yes'
            
        doc.save()

        messages.success(request,"Successfully edited Learning Programme Document")        

        return redirect('college:learning_programme_documents',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_document_delete(request,pk,doc_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = LearningProgrammeDocument.objects.get(id = doc_pk)
            lp.delete()
            messages.success(request,"Successfully deleted learning programme document")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_documents',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



class LearningProgrammeELOList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_elos.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeELOList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeELO.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_elo_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeELOForm(request.POST)
        if form.is_valid():
            elo = form.save(commit=False)
            elo.learning_programme_id = pk
            elo.save()

            messages.success(request,"Successfully added learning programme Exit Level Outcome")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_elos',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_elo_edit(request,pk,elo_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        elo = LearningProgrammeELO.objects.get(id = elo_pk)
        form = LearningProgrammeELOForm(request.POST,instance = elo)
        if form.is_valid():
            elo = form.save(commit=False)
            elo.learning_programme_id = pk
            elo.save()

            messages.success(request,"Successfully edited Learning Programme Exit Level Outcome ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_elos',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_elo_delete(request,pk,elo_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            elo = LearningProgrammeELO.objects.get(id = elo_pk)
            elo.delete()
            messages.success(request,"Successfully deleted learning programme Exit Level Outcome")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_elos',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def learning_programme_elo_assessment_criteria_add(request,pk,elo_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeELOAssessmentCriteriaForm(request.POST)
        if form.is_valid():
            elo = form.save(commit=False)
            elo.elo_id = elo_pk
            elo.save()

            messages.success(request,"Successfully added learning programme Exit Level Outcome Assessment Criteria")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_elos',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_elo_assessment_criteria_edit(request,pk,elo_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        ass_instance = LearningProgrammeELOAssessmentCriteria.objects.get(id = assessment_pk)
        form = LearningProgrammeELOAssessmentCriteriaForm(request.POST,instance=ass_instance)
        if form.is_valid():
            elo = form.save(commit=False)
            elo.elo_id = elo_pk
            elo.save()

            messages.success(request,"Successfully edited learning programme Exit Level Outcome Assessment Criteria")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_elos',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def learning_programme_elo_assessment_criteria_delete(request,pk,elo_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            elo = LearningProgrammeELOAssessmentCriteria.objects.get(id = assessment_pk)
            elo.delete()
            messages.success(request,"Successfully deleted learning programme Exit Level Outcome Assessment Criteria")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_elos',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class LearningProgrammeCompetencyList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_competencies.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCompetencyList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCompetency.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_competency_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeCompetencyForm(request.POST)
        if form.is_valid():
            competency = form.save(commit=False)
            competency.learning_programme_id = pk
            competency.save()

            messages.success(request,"Successfully added learning programme Competency")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_competencies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_competency_edit(request,pk,competency_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        competency = LearningProgrammeCompetency.objects.get(id = competency_pk)
        form = LearningProgrammeCompetencyForm(request.POST,instance = competency)
        if form.is_valid():
            competency = form.save(commit=False)
            competency.learning_programme_id = pk
            competency.save()

            messages.success(request,"Successfully edited Learning Programme Comptency ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_competencies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_competency_delete(request,pk,competency_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            competency = LearningProgrammeCompetency.objects.get(id = competency_pk)
            competency.delete()
            messages.success(request,"Successfully deleted learning programme Competency")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_competencies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_competency_breakdown_add(request,pk,competency_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeCompetencyBreakdownForm(request.POST)
        if form.is_valid():
            breakdown = form.save(commit=False)
            breakdown.competency_id = competency_pk
            breakdown.save()

            messages.success(request,"Successfully added Learning Programme Comptency breakdown")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_competencies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_competency_breakdown_edit(request,pk,competency_pk,breakdown_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        breakdown = LearningProgrammeCompetencyBreakdown.objects.get(id = breakdown_pk)
        form = LearningProgrammeCompetencyBreakdownForm(request.POST,instance = breakdown)
        if form.is_valid():
            breakdown = form.save(commit=False)
            breakdown.competency_id = competency_pk
            breakdown.save()

            messages.success(request,"Successfully edited Learning Programme Comptency breakdown")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_competencies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_competency_breakdown_delete(request,pk,competency_pk,breakdown_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        try:
            breakdown = LearningProgrammeCompetencyBreakdown.objects.get(id = breakdown_pk)
            breakdown.delete()
            messages.success(request,"Successfully deleted learning programme Competency Breakdown")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_competencies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    




class LearningProgrammeSimulationThemeList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_simulation_themes.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCompetencyList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCompetency.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_simulation_theme_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeSimulationThemeForm(request.POST)
        if form.is_valid():
            theme = form.save(commit=False)
            theme.learning_programme_id = pk
            theme.save()

            messages.success(request,"Successfully added learning programme Theme")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_simulation_themes',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_simulation_theme_edit(request,pk,theme_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        theme = LearningProgrammeSimulationTheme.objects.get(id = theme_pk)
        form = LearningProgrammeSimulationThemeForm(request.POST,instance = theme)
        if form.is_valid():
            theme = form.save(commit=False)
            theme.learning_programme_id = pk
            theme.save()

            messages.success(request,"Successfully edited Learning Programme Theme ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_simulation_themes',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_simulation_theme_delete(request,pk,theme_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            theme = LearningProgrammeSimulationTheme.objects.get(id = theme_pk)
            theme.delete()
            messages.success(request,"Successfully deleted learning programme theme")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_simulation_themes',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_simulation_theme_activities_add(request,pk,theme_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeSimulationThemeActivitiesForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.theme_id = theme_pk
            activity.save()

            messages.success(request,"Successfully added Learning Programme  Theme Activity")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_simulation_themes',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_simulation_theme_activities_edit(request,pk,theme_pk,activity_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        activity = LearningProgrammeSimulationThemeActivities.objects.get(id = activity_pk)
        form = LearningProgrammeSimulationThemeActivitiesForm(request.POST,instance = activity)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.theme_id = theme_pk
            activity.save()

            messages.success(request,"Successfully edited Learning Programme Theme Activity")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_simulation_themes',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def learning_programme_simulation_theme_activities_delete(request,pk,theme_pk,activity_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        try:
            breakdown = LearningProgrammeSimulationThemeActivities.objects.get(id = activity_pk)
            breakdown.delete()
            messages.success(request,"Successfully deleted learning programme theme activity")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_simulation_themes',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    





class LearningProgrammeModuleList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeModuleList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeModule.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['learning_programme_menu'] = '--active'
        context['nqf_levels'] = NQFLevel.objects.all()
        return context

@login_required()
def learning_programme_module_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.learning_programme_id = pk
            module.nqf_level_id = request.POST['nqf_level']
            module.save()

            messages.success(request,"Successfully added learning programme Module")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_module_edit(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        module = LearningProgrammeModule.objects.get(id = module_pk)
        form = LearningProgrammeModuleForm(request.POST,instance = module)
        if form.is_valid():
            module = form.save(commit=False)
            module.learning_programme_id = pk
            module.nqf_level_id = request.POST['nqf_level']
            module.save()

            messages.success(request,"Successfully edited Learning Programme Module ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_module_delete(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            module = LearningProgrammeModule.objects.get(id = module_pk)
            module.delete()
            messages.success(request,"Successfully deleted learning programme Module")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_module_prerequisite_add(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        pass_check = True

        module = LearningProgrammeModule.objects.get(id = module_pk)
        #check if prerequisite exists
        check = LearningProgrammeModulePrerequisite.objects.filter(module=module,prerequisite_id = request.POST['prerequisite'])
        if check.exists():
            messages.warning(request,"Selected Module is already a prerequisite ")
            pass_check = False
        
        check_postrequisite = LearningProgrammeModulePrerequisite.objects.filter(prerequisite=module,module_id = request.POST['prerequisite'])
        if check_postrequisite.exists():
            pass_check = False
            messages.warning(request,'Selected Module is already a postrequisite for the same module')
            
        if pass_check:
            LearningProgrammeModulePrerequisite.objects.create(module=module,prerequisite_id = request.POST['prerequisite'])
            messages.success(request,"Selected added prerequisite")
        

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def learning_programme_module_prerequisite_delete(request,pk,module_pk,prerequisite_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            prerequisite = LearningProgrammeModulePrerequisite.objects.get(id = prerequisite_pk)
            prerequisite.delete()
            messages.success(request,"Successfully deleted learning programme Module prerequisite")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def learning_programme_module_formative_add(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeModuleFormativeForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.module_id = module_pk
            assessment.save()

            messages.success(request,"Successfully added Assessment")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_module_formative_edit(request,pk,module_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        assessment = LearningProgrammeModuleFormative.objects.get(id = assessment_pk)
        form = LearningProgrammeModuleFormativeForm(request.POST,instance = assessment)
        if form.is_valid():
            form.save()

            messages.success(request,"Successfully edited Assessment ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_module_formative_delete(request,pk,module_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            assessment = LearningProgrammeModuleFormative.objects.get(id = assessment_pk)
            assessment.delete()
            messages.success(request,"Successfully deleted Assessment")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class LearningProgrammeModuleStudyUnitList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_module_studyunits.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeModuleStudyUnitList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeModuleStudyUnit.objects.filter(module_id = self.kwargs['module_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = LearningProgrammeModule.objects.get(id = self.kwargs['module_pk'])
        context['learning_programme_menu'] = '--active'
        return context

@login_required()
def learning_programme_module_studyunit_add(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeModuleStudyUnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.module_id = module_pk
            unit.save()

            messages.success(request,"Successfully added learning programme Module Study Unit")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_module_studyunits',pk=pk,module_pk=module_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_module_studyunit_edit(request,pk,module_pk,unit_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        unit = LearningProgrammeModuleStudyUnit.objects.get(id = unit_pk)
        form = LearningProgrammeModuleStudyUnitForm(request.POST,instance = unit)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.module_id = module_pk
            unit.save()

            messages.success(request,"Successfully edited Learning Programme Module Study Unit")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_module_studyunits',pk=pk,module_pk=module_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_module_studyunit_delete(request,pk,module_pk,unit_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            module = LearningProgrammeModuleStudyUnit.objects.get(id = unit_pk)
            module.delete()
            messages.success(request,"Successfully deleted learning programme Module Study Unit")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_module_studyunits',pk=pk,module_pk=module_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def learning_programme_module_studyunit_section_add(request,pk,module_pk,unit_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeModuleStudyUnitSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.study_unit_id = unit_pk
            section.save()

            messages.success(request,"Successfully edited Learning Programme Module Study Unit Section")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_module_studyunits',pk=pk,module_pk=module_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def learning_programme_module_studyunit_section_edit(request,pk,module_pk,unit_pk,section_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        section = LearningProgrammeModuleStudyUnitSection.objects.get(id = section_pk)
        form = LearningProgrammeModuleStudyUnitSectionForm(request.POST,instance = section)
        if form.is_valid():
            section = form.save(commit=False)
            section.study_unit_id = unit_pk
            section.save()

            messages.success(request,"Successfully edited Learning Programme Module Study Unit Section")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_module_studyunits',pk=pk,module_pk=module_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def learning_programme_module_studyunit_section_delete(request,pk,module_pk,unit_pk,section_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            module = LearningProgrammeModuleStudyUnitSection.objects.get(id = section_pk)
            module.delete()
            messages.success(request,"Successfully deleted learning programme Module Study Unit Section")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_module_studyunits',pk=pk,module_pk=module_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
class LearningProgrammeCohortList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohorts.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCohort.objects.filter(learning_programme_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['periods'] = LearningProgrammePeriod.objects.filter(learning_programme_id = self.kwargs['pk'])
        context['cohort_menu'] = '--active'
        return context

@login_required()
def learning_programme_cohort_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        form = LearningProgrammeCohortForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.learning_programme_id = pk
            module.save()

            messages.success(request,"Successfully added learning programme cohort")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohorts',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_edit(request,pk,cohort_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        cohort = LearningProgrammeCohort.objects.get(id = cohort_pk)
        form = LearningProgrammeCohortForm(request.POST,instance = cohort)
        if form.is_valid():
            cohort = form.save(commit=False)
            cohort.learning_programme_id = pk
            cohort.save()

            messages.success(request,"Successfully edited Learning Programme cohort ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohorts',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_delete(request,pk,cohort_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            cohort = LearningProgrammeCohort.objects.get(id = cohort_pk)
            cohort.delete()
            messages.success(request,"Successfully deleted learning programme cohort")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohorts',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class LearningProgrammeCohortRegistrationPeriodList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_period.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationPeriodList, self).get(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.logged_in_role_id == 2 or self.request.user.logged_in_role_id == 1:
            return  LearningProgrammeCohortRegistrationPeriod.objects.filter(learning_programme_cohort_id = self.kwargs['pk'])
        elif self.request.user.logged_in_role_id == 6:
            return  LearningProgrammeCohortRegistrationPeriod.objects.filter(learning_programme_cohort_id = self.kwargs['pk'],programme_coordinator = self.request.user)
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = self.kwargs['pk'])
        context['learning_programme_cohort'] = learning_programme_cohort 
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['periods'] = LearningProgrammePeriod.objects.filter(learning_programme_id = learning_programme_cohort.learning_programme_id)
        context['cohort_menu'] = '--active'
        
        role = Role.objects.get(id = 6) 
        coordinators = role.user_set.all()
        context['coordinators'] = coordinators
        
        return context


@login_required()
def learning_programme_cohort_registration_period_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:
        
        check_period = False

        #check if cohort has period  - This has been removed

        #check_period = LearningProgrammeCohortRegistrationPeriod.objects.filter(period__id = request.POST['period'],learning_programme_cohort__id = pk).exists()

        if check_period:
            messages.warning(request,'Period added previously')
        else:
            form = LearningProgrammeCohortRegistrationPeriodForm(request.POST)
            if form.is_valid():
                period = form.save(commit=False)
                period.period_id = request.POST['period']
                period.learning_programme_cohort_id = pk
                period.save()

                messages.success(request,"Successfully added learning programme cohort registration period")
                modules = period.learning_programme_cohort.learning_programme.modules.all()
                
                for module in modules:
                    check_p = CohortRegistrationPeriodModule.objects.filter(module = module,cohort_registration_period = period).exists()

                    if check_p:
                        messages.warning(request,'Module added previously')
                    else:
                        added_module = CohortRegistrationPeriodModule.objects.create(
                            module = module,
                            cohort_registration_period = period,     
                            entrance_year_mark = module.entrance_year_mark,
                            summative_weight = module.summative_weight,
                            assignment_weight = module.assignment_weight,
                            test_weight = module.test_weight               
                        )
                        
                        CohortRegistrationPeriodModuleFormative.objects.filter(module = added_module).delete()
                            
                        for assessment in module.formative.all():
                            #remove all assessments for that module and copy over the template
                            CohortRegistrationPeriodModuleFormative.objects.create(
                                module = added_module,
                                assessment_type = assessment.assessment_type,
                                title = assessment.title,
                                weight = assessment.weight                        
                            )
            else:
                messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_periods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_period_edit(request,pk,period_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = period_pk)
        form = LearningProgrammeCohortRegistrationPeriodForm(request.POST,instance = period)
        if form.is_valid():
            period = form.save(commit=False)
            period.period_id = request.POST['period']
            period.save()

            messages.success(request,"Successfully edited Learning Programme cohort registration period")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_periods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def learning_programme_cohort_registration_period_delete(request,pk,period_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = period_pk)
            period.delete()
            messages.success(request,"Successfully deleted learning programme cohort registration period")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_periods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def learning_programme_cohort_registration_period_programme_coordinator(request,pk,period_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = period_pk)
        period.programme_coordinator_id = request.POST['programme_coordinator']
        period.save()

        messages.success(request,"Successfully assigned programme coordinator")
     
        return redirect('college:learning_programme_cohort_registration_periods',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')





class LearningProgrammeCohortRegistrationCompulsoryProceduresList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_compulsory_procedures.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationCompulsoryProceduresList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationCompulsoryProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

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


@login_required()
def learning_programme_cohort_registration_compulsory_procedures_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if cohort ihas period

        check_period = CohortRegistrationCompulsoryProcedure.objects.filter(procedure__id = request.POST['procedure'],cohort_registration_period__id = pk).exists()

        if check_period:
            messages.warning(request,'Period added previously')
        else:
            form = CohortRegistrationCompulsoryProcedureForm(request.POST)
            if form.is_valid():
                period = form.save(commit=False)
                period.procedure_id = request.POST['procedure']
                period.cohort_registration_period_id = pk
                period.save()

                messages.success(request,"Successfully added compulsory procedure")
            else:
                messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_compulsory_procedures',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_compulsory_procedures_edit(request,pk,procedure_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        procedure = CohortRegistrationCompulsoryProcedure.objects.get(id = procedure_pk)
        form = CohortRegistrationCompulsoryProcedureForm(request.POST,instance = procedure)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.procedure_id = request.POST['procedure']
            procedure.save()

            messages.success(request,"Successfully edited compulsory procedure")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_compulsory_procedures',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_compulsory_procedures_delete(request,pk,procedure_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            procedure = CohortRegistrationCompulsoryProcedure.objects.get(id = procedure_pk)
            procedure.delete()
            messages.success(request,"Successfully deleted compulsory procedure")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_compulsory_procedures',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


class LearningProgrammeCohortRegistrationProceduresList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_procedures.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationProceduresList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

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

@login_required()
def learning_programme_cohort_registration_procedures_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if cohort ihas period
        
        procedures = request.POST.getlist('procedures[]')
        for p_id in procedures:
            check_p = CohortRegistrationProcedure.objects.filter(procedure__id = p_id,cohort_registration_period__id = pk).exists()

            if check_p:
                messages.warning(request,'Period added previously')
            else:
                CohortRegistrationProcedure.objects.create(
                    procedure_id = p_id,
                    cohort_registration_period_id = pk,                    
                )

        messages.success(request,"Successfully added procedures")
            
        return redirect('college:learning_programme_cohort_registration_procedures',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_procedures_edit(request,pk,procedure_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        procedure = CohortRegistrationProcedure.objects.get(id = procedure_pk)
        form = CohortRegistrationProcedureForm(request.POST,instance = procedure)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.save()

            messages.success(request,"Successfully edited procedure")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_procedures',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_procedures_delete(request,pk,procedure_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            procedure = CohortRegistrationProcedure.objects.get(id = procedure_pk)
            procedure.delete()
            messages.success(request,"Successfully deleted compulsory procedure")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_procedures',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

class BackgroundThreadCopyAssessments(threading.Thread):
    
    def __init__(self,request,learning_programme_cohort_registration_period):
        self.learning_programme_cohort_registration_period = learning_programme_cohort_registration_period 
        self.request = request

        threading.Thread.__init__(self)

    def run(self):
        for procedure in self.learning_programme_cohort_registration_period.cohort_period_procedures.all():
            #check if procedure has an assessment
            if procedure.procedure.assessments.count() > 0:
                CohortRegistrationProcedureTaskAssessment.objects.filter(task = procedure).delete()
                    
                for assessment in procedure.procedure.assessments.all():
                    #remove all assessments for that procedure and copy over the template
                    CohortRegistrationProcedureTaskAssessment.objects.create(
                        task = procedure,
                        question = assessment.question,
                        question_type = assessment.question_type,
                        number = assessment.number,
                        penalty = assessment.penalty,                  
                    )
        email_body = 'Assessments have been copied over'
        title = 'Procedure Assessments Copied'
        name = self.request.user.first_name
        to = self.request.user.email
        send_email_general(to,name,title,email_body)

@login_required()
def copy_procedure_tasks_assessments(request,pk):
    '''
    copy all the procedure tasks assessments
    '''
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        
        BackgroundThreadCopyAssessments(request,learning_programme_cohort_registration_period).start()
        
        messages.success(request,'The assessments will be copied over and an email will be sent to you once done')
     
        return redirect('college:learning_programme_cohort_registration_procedures',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
       

class LearningProgrammeCohortRegistrationProceduresStaffList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_procedures_staff.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1  and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationProceduresStaffList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedure.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['procedures'] = ClinicalProcedureThemeTask.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        
        role = Role.objects.get(id = 4) 
        all_lecturers = role.user_set.all()
        context['lecturers'] = all_lecturers
        
        role = Role.objects.get(id = 5) 
        all_facilitators = role.user_set.all()
        context['facilitators'] = all_facilitators
        
        return context



@login_required()
def assign_procedure_staff(request,pk):

    '''
    Assign advisor
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        lecturer,facilitator = None,None
        
        procedures = request.POST.getlist('procedures_selected[]')
        
        facilitator_type = 'Demonstration'
        
        if 'facilitator_type' in request.POST:
            facilitator_type = request.POST['facilitator_type']            

        if 'lecturer' in request.POST and request.POST['lecturer'] != "":
            lecturer = User.objects.get(id = request.POST['lecturer'])
            
        if 'clinical_facilitator' in request.POST and request.POST['clinical_facilitator'] != "":
            facilitator = User.objects.get(id = request.POST['clinical_facilitator'])
            
        for app_pk in procedures:
            procedure = CohortRegistrationProcedure.objects.get(id = app_pk)
            
            if facilitator_type == 'Demonstration':
                if lecturer:          
                    procedure.lecturer_demonstration = lecturer                    
                if facilitator:
                    procedure.clinical_facilitator_demonstration = facilitator
            
            elif facilitator_type == 'Assessment':
                if lecturer:          
                    procedure.lecturer = lecturer                    
                if facilitator:
                    procedure.clinical_facilitator = facilitator
                
            procedure.save()

        messages.success(request,"Successfully assigned staff to selected procedures")

        return redirect('college:learning_programme_cohort_registration_procedures_staff',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class LearningProgrammeCohortRegistrationProceduresSummativeList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_procedures_summative.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationProceduresSummativeList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

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

@login_required()
def learning_programme_cohort_registration_procedures_summative_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if cohort ihas period
        
        procedures = request.POST.getlist('procedures[]')
        for p_id in procedures:
            check_p = CohortRegistrationProcedureSummative.objects.filter(procedure__id = p_id,cohort_registration_period__id = pk).exists()

            if check_p:
                messages.warning(request,'Period added previously')
            else:
                CohortRegistrationProcedureSummative.objects.create(
                    procedure_id = p_id,
                    cohort_registration_period_id = pk,    
                    weights = request.POST['weights']                
                )

        messages.success(request,"Successfully added procedures")
            
        return redirect('college:learning_programme_cohort_registration_procedures_summative',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_procedures_summative_edit(request,pk,procedure_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        procedure = CohortRegistrationProcedureSummative.objects.get(id = procedure_pk)
        form = CohortRegistrationProcedureSummativeForm(request.POST,instance = procedure)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.save()

            messages.success(request,"Successfully edited procedure")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_procedures_summative',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_procedures_summative_delete(request,pk,procedure_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            procedure = CohortRegistrationProcedureSummative.objects.get(id = procedure_pk)
            procedure.delete()
            messages.success(request,"Successfully deleted compulsory procedure")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_procedures_summative',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

class BackgroundThreadCopySummativeAssessments(threading.Thread):
    
    def __init__(self,request,learning_programme_cohort_registration_period):
        self.learning_programme_cohort_registration_period = learning_programme_cohort_registration_period 
        self.request = request

        threading.Thread.__init__(self)

    def run(self):
        for procedure in self.learning_programme_cohort_registration_period.cohort_period_summative_procedures.all():
            #check if procedure has an assessment
            if procedure.procedure.assessments.count() > 0:
                CohortRegistrationProcedureSummativeTaskAssessment.objects.filter(task = procedure).delete()
                    
                for assessment in procedure.procedure.assessments.all():
                    #remove all assessments for that procedure and copy over the template
                    CohortRegistrationProcedureSummativeTaskAssessment.objects.create(
                        task = procedure,
                        question = assessment.question,
                        question_type = assessment.question_type,
                        number = assessment.number,
                        penalty = assessment.penalty,                  
                    )
        email_body = 'Assessments have been copied over'
        title = 'Procedure Assessments Copied'
        name = self.request.user.first_name
        to = self.request.user.email
        send_email_general(to,name,title,email_body)

@login_required()
def copy_procedure_summative_tasks_assessments(request,pk):
    '''
    copy all the procedure tasks assessments
    '''
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        
        BackgroundThreadCopySummativeAssessments(request,learning_programme_cohort_registration_period).start()
        
        messages.success(request,'The assessments will be copied over and an email will be sent to you once done')
     
        return redirect('college:learning_programme_cohort_registration_procedures_summative',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
       

class LearningProgrammeCohortRegistrationProceduresSummativeStaffList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_procedures_summative_staff.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationProceduresSummativeStaffList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedureSummative.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['procedures'] = ClinicalProcedureThemeTask.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        
        role = Role.objects.get(id = 4) 
        all_lecturers = role.user_set.all()
        context['lecturers'] = all_lecturers
        
        role = Role.objects.get(id = 5) 
        all_facilitators = role.user_set.all()
        context['facilitators'] = all_facilitators
        
        return context



@login_required()
def assign_procedure_summative_staff(request,pk):

    '''
    Assign advisor
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        assessor,facilitator = None,None
        
        procedures = request.POST.getlist('procedures_selected[]')
                     

        if 'assessor' in request.POST and request.POST['assessor'] != "":
            assessor = User.objects.get(id = request.POST['assessor'])
            
        if 'clinical_facilitator' in request.POST and request.POST['clinical_facilitator'] != "":
            facilitator = User.objects.get(id = request.POST['clinical_facilitator'])
            
        for app_pk in procedures:
            procedure = CohortRegistrationProcedureSummative.objects.get(id = app_pk)
            
            if assessor:          
                procedure.assessor = assessor                    
            if facilitator:
                procedure.clinical_facilitator = facilitator
                
            procedure.save()

        messages.success(request,"Successfully assigned staff to selected procedures")

        return redirect('college:learning_programme_cohort_registration_procedures_summative_staff',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class LearningProgrammeCohortRegistrationProceduresSummativeModeratorList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_procedures_summative_moderators.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationProceduresSummativeModeratorList, self).get(*args, **kwargs)

    def get_queryset(self):
        period =  LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        return period.summative_procedures_moderators.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        
        context['moderators'] = Moderator.objects.all()
        
        return context



@login_required()
def assign_procedure_summative_moderators(request,pk):

    '''
    Assign moderators
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        
        
        moderators = request.POST.getlist('moderators[]')
             
        for app_pk in moderators:
            moderator = Moderator.objects.get(id = app_pk)
            
            period.summative_procedures_moderators.add(moderator)
                
            period.save()

        messages.success(request,"Successfully assigned moderators")

        return redirect('college:learning_programme_cohort_registration_procedures_summative_moderators',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def delete_procedure_summative_moderators(request,pk,moderator_pk):

    '''
    delete moderator
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)        
        
        moderator = Moderator.objects.get(id = moderator_pk)
        
        period.summative_procedures_moderators.remove(moderator)
             
        period.save()

        messages.success(request,"Successfully removed moderator")

        return redirect('college:learning_programme_cohort_registration_procedures_summative_moderators',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



class LearningProgrammeCohortRegistrationProcedureSummativeAssessmentList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_procedure_summative_assessments.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationProcedureSummativeAssessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedureSummativeTaskAssessment.objects.filter(task_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = CohortRegistrationProcedureSummative.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort_registration_period = task.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['procedures'] = ClinicalProcedureThemeTask.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        context['task'] = task
        return context    

@login_required()
def registration_procedure_summative_tasks_assessments_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        form = CohortRegistrationProcedureSummativeTaskAssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)  
            assessment.task_id = pk  
            assessment.save()                   

            messages.success(request,"Successfully added Assessment details")
        else:
            messages.warning(request,form.errors)

        return redirect('college:procedure_summative_tasks_assessments',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def registration_procedure_summative_tasks_assessments_edit(request,pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        block_instance = CohortRegistrationProcedureSummativeTaskAssessment.objects.get(id = assessment_pk)
        form = CohortRegistrationProcedureSummativeTaskAssessmentForm(request.POST,instance = block_instance)
        if form.is_valid():
            form.save()
            
            messages.success(request,"Successfully edited Assessment")
        else:
            messages.warning(request,form.errors)

        return redirect('college:procedure_summative_tasks_assessments',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def registration_procedure_summative_tasks_assessments_delete(request,pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            i_instance = CohortRegistrationProcedureSummativeTaskAssessment.objects.get(id = assessment_pk)
            i_instance.delete()
            messages.success(request,"Successfully deleted Assessment")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:procedure_summative_tasks_assessments',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    









class LearningProgrammeCohortRegistrationModulesList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_modules.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationModulesList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModule.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['modules'] = learning_programme_cohort.learning_programme.modules.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context
    

@login_required()
def learning_programme_cohort_registration_modules_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        #check if cohort ihas period
        
        modules = request.POST.getlist('modules[]')
        for p_id in modules:
            module = LearningProgrammeModule.objects.get(id = p_id)
            check_p = CohortRegistrationPeriodModule.objects.filter(module__id = p_id,cohort_registration_period__id = pk).exists()

            if check_p:
                messages.warning(request,'Module added previously')
            else:
                added_module = CohortRegistrationPeriodModule.objects.create(
                    module_id = p_id,
                    cohort_registration_period_id = pk,     
                    entrance_year_mark = module.entrance_year_mark,
                    summative_weight = module.summative_weight,
                    assignment_weight = module.assignment_weight,
                    test_weight = module.test_weight               
                )
                
                CohortRegistrationPeriodModuleFormative.objects.filter(module = added_module).delete()
                    
                for assessment in module.formative.all():
                    #remove all assessments for that module and copy over the template
                    CohortRegistrationPeriodModuleFormative.objects.create(
                        module = added_module,
                        assessment_type = assessment.assessment_type,
                        title = assessment.title,
                        weight = assessment.weight                        
                    )

        messages.success(request,"Successfully added module")
            
        return redirect('college:learning_programme_cohort_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_modules_edit(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        module = CohortRegistrationPeriodModule.objects.get(id = module_pk)
        form = CohortRegistrationPeriodModuleForm(request.POST,instance = module)
        if form.is_valid():
            module = form.save(commit=False)
            module.save()

            messages.success(request,"Successfully edited module")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_modules_delete(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            module = CohortRegistrationPeriodModule.objects.get(id = module_pk)
            module.delete()
            messages.success(request,"Successfully removed Module")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

class BackgroundThreadCopyModuleAssessments(threading.Thread):
    
    def __init__(self,request,learning_programme_cohort_registration_period):
        self.learning_programme_cohort_registration_period = learning_programme_cohort_registration_period 
        self.request = request

        threading.Thread.__init__(self)

    def run(self):
        for module in self.learning_programme_cohort_registration_period.modules.all():
            #check if module has an assessment
            if module.module.formative.count() > 0:
                CohortRegistrationPeriodModuleFormative.objects.filter(module = module).delete()
                    
                for assessment in module.module.formative.all():
                    #remove all assessments for that module and copy over the template
                    CohortRegistrationPeriodModuleFormative.objects.create(
                        module = module,
                        assessment_type = assessment.assessment_type,
                        title = assessment.title,
                        weight = assessment.weight                        
                    )
        email_body = 'Assessments have been copied over'
        title = 'Module Assessments Copied'
        name = self.request.user.first_name
        to = self.request.user.email
        send_email_general(to,name,title,email_body)

@login_required()
def copy_modules_assessments(request,pk):
    '''
    copy all the module assessments
    '''
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        
        BackgroundThreadCopyModuleAssessments(request,learning_programme_cohort_registration_period).start()
        
        messages.success(request,'The assessments will be copied over and an email will be sent to you once done')
     
        return redirect('college:learning_programme_cohort_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
       

@login_required()
def learning_programme_cohort_registration_module_formative_add(request,pk,module_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        form = CohortRegistrationPeriodModuleFormativeForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.module_id = module_pk
            assessment.save()

            messages.success(request,"Successfully added Assessment")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_module_formative_edit(request,pk,module_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        assessment = CohortRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
        form = CohortRegistrationPeriodModuleFormativeForm(request.POST,instance = assessment)
        if form.is_valid():
            form.save()

            messages.success(request,"Successfully edited Assessment ")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_module_formative_delete(request,pk,module_pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            assessment = CohortRegistrationPeriodModuleFormative.objects.get(id = assessment_pk)
            assessment.delete()
            messages.success(request,"Successfully deleted Assessment")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_modules',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



class LearningProgrammeCohortRegistrationModulesStaffList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_modules_staff.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationModulesStaffList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModule.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        
        role = Role.objects.get(id = 4) 
        all_lecturers = role.user_set.all()
        context['lecturers'] = all_lecturers        
        context['moderators'] = Moderator.objects.all()
                
        return context



@login_required()
def assign_module_staff(request,pk):

    '''
    Assign lecturer
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        lecturer = None
        
        modules = request.POST.getlist('modules_selected[]')
        
        if 'lecturer' in request.POST and request.POST['lecturer'] != "":
            lecturer = User.objects.get(id = request.POST['lecturer'])
                        
        for app_pk in modules:
            module = CohortRegistrationPeriodModule.objects.get(id = app_pk)  
            if lecturer:          
                module.lecturer = lecturer
                            
            module.save()

        messages.success(request,"Successfully assigned staff to selected modules")

        return redirect('college:learning_programme_cohort_registration_modules_staff',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



class LearningProgrammeCohortRegistrationModulesModeratorList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_modules_moderator.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationModulesModeratorList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodModule.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
              
        context['moderators'] = Moderator.objects.all()
                
        return context



@login_required()
def assign_module_moderator(request,pk):

    '''
    Assign lecturer
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        lecturer = None
        
        modules = request.POST.getlist('modules_selected[]')
        
        if 'moderator' in request.POST and request.POST['moderator'] != "":
            moderator = Moderator.objects.get(id = request.POST['moderator'])
                        
        for app_pk in modules:
            module = CohortRegistrationPeriodModule.objects.get(id = app_pk)  
            if moderator:          
                module.moderator = moderator
                            
            module.save()

        messages.success(request,"Successfully assigned moderator to selected modules")

        return redirect('college:learning_programme_cohort_registration_modules_moderator',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



class LearningProgrammeCohortRegistrationModuleStudentList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_modules_students.html'
    context_object_name = 'students'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 6 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 2:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationModuleStudentList, self).get(*args, **kwargs)

    def get_queryset(self):
        students = list(StudentRegistrationModule.
                        objects.
                        filter(module_id = self.kwargs['module_pk']).
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
                            'final_mark',
                           )
                        )
        return  students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['module'] = CohortRegistrationPeriodModule.objects.get(id = self.kwargs['module_pk'])
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context



@login_required()
def learning_programme_cohort_module_moderators_report_view(request,pk):
    
    if request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        
        moderator = None

        module = CohortRegistrationPeriodModule.objects.get(id = pk)
        learning_programme_cohort_period = module.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_period.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme
        
        check_moderator = Moderator.objects.filter(user = request.user)
        if check_moderator.exists():
            moderator = check_moderator.first()
                        
        assessment = []
        
        #check if report exists

        check_report_user = CohortRegistrationPeriodModuleModerationReport.objects.filter(module = module)

        if check_report_user.exists():
            report = check_report_user.first()
        else:
            report = CohortRegistrationPeriodModuleModerationReport.objects.create(module = module,moderator=moderator)
        
        assessments = list(LearningProgrammePeriodModerationCriteria.
                           objects.
                           filter(
                               learning_programme_period = module.cohort_registration_period.period,                               
                           ).values('criteria','id','question_type','number','role'))
       
        for ass in assessments:
            ass_map = {'id':ass['id'],
                       'criteria':ass['criteria'],
                       'question_type':ass['question_type'],
                       'number':'.'.join(str(int(part)) for part in ass['number'].split('.')),
                       'original_number':ass['number'],
                       'role':ass['role']}
            
            
            check_answer = (CohortRegistrationPeriodModuleModerationReportAnswers.
                                objects.
                                filter(
                                    report = report,
                                    assessment_id = ass['id']
                                ))
            
            if check_answer.exists():
                answer = check_answer.first()
            
                ass_map['answer_id'] = answer.id
                ass_map['answer_answer'] = answer.answer
                ass_map['answer_comment'] = answer.remarks
                
            
            
            assessment.append(ass_map)

        return render(request,'college/learing_programme_cohort_registration_modules_moderation.html',{
                                                                          'learning_programme_cohort':learning_programme_cohort,
                                                                          'learning_programme':learning_programme,
                                                                          'learning_programme_cohort_period':learning_programme_cohort_period,
                                                                          'module':module,
                                                                          'report':report,
                                                                          'cohort_menu':'--active',
                                                                          'assessment':assessment,})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def learning_programme_cohort_module_student_edit_final_mark(request,pk):
    
    if request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        
        registration = StudentRegistrationModule.objects.get(id = pk)
        registration.final_mark = request.POST['final_mark']
        registration.marks_edited_reason = request.POST['marks_edited_reason']
        registration.save()
        
        messages.success(request,'Successfully edited marks')
        
        return redirect('college:learning_programme_cohort_registration_module_students', pk=registration.registration.registration_period_id, module_pk = registration.module_id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
class LearningProgrammeCohortRegistrationProcedureAssessmentList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_procedure_assessments.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6 and self.request.user.logged_in_role_id != 4:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationProcedureAssessmentList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationProcedureTaskAssessment.objects.filter(task_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = CohortRegistrationProcedure.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort_registration_period = task.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['procedures'] = ClinicalProcedureThemeTask.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        context['task'] = task
        return context    

@login_required()
def registration_procedure_tasks_assessments_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 4:

        form = CohortRegistrationProcedureTaskAssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)  
            assessment.task_id = pk  
            assessment.save()                   

            messages.success(request,"Successfully added Assessment details")
        else:
            messages.warning(request,form.errors)

        return redirect('college:procedure_tasks_assessments',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def registration_procedure_tasks_assessments_edit(request,pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 4:

        block_instance = CohortRegistrationProcedureTaskAssessment.objects.get(id = assessment_pk)
        form = CohortRegistrationProcedureTaskAssessmentForm(request.POST,instance = block_instance)
        if form.is_valid():
            form.save()
            
            messages.success(request,"Successfully edited Assessment")
        else:
            messages.warning(request,form.errors)

        return redirect('college:procedure_tasks_assessments',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def registration_procedure_tasks_assessments_delete(request,pk,assessment_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 4:

        try:
            i_instance = CohortRegistrationProcedureTaskAssessment.objects.get(id = assessment_pk)
            i_instance.delete()
            messages.success(request,"Successfully deleted Assessment")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:procedure_tasks_assessments',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
 

  

class LearningProgrammeBlockTemplateList(LoginRequiredMixin,ListView):
    template_name = 'college/block_template.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeBlockTemplateList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeBlockTemplate.objects.filter(period__id = self.kwargs['period_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['learning_programme_menu'] = '--active'
        context['learning_programme'] = LearningProgramme.objects.get(id = self.kwargs['pk'])
        context['period'] = LearningProgrammePeriod.objects.get(id = self.kwargs['period_pk'])
        context['blocks'] = ProgarmmeBlock.objects.all()
        
        return context

@login_required()
def learning_programme_block_template_add(request,pk,period_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        #check academic week exists
        
        check_week_exists = LearningProgrammeBlockTemplate.objects.filter(period_id = period_pk,academic_week=request.POST['academic_week']).exists()

        if check_week_exists:
            messages.warning(request,'You cannot have a duplicate academic week')
        else:
            form = LearningProgrammeBlockTemplateForm(request.POST)
            if form.is_valid():
                block_instance = form.save(commit = False)
                block_instance.learning_programme_id = pk
                block_instance.period_id = period_pk
                if 'block' in request.POST:
                    block_instance.block_id = request.POST['block']
                    
                if 'facility_type' in request.POST:
                    block_instance.facility_type = request.POST['facility_type']
                    
                if 'time_period' in request.POST:
                    block_instance.time_period = request.POST['time_period']

                block_instance.save()

                messages.success(request,"Successfully added  Template Block")
            else:
                messages.warning(request,form.errors)

        return redirect('college:lp_block_template',pk=pk,period_pk=period_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_block_template_edit(request,pk,period_pk,block_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        block_instance = LearningProgrammeBlockTemplate.objects.get(id = block_pk)
        form = LearningProgrammeBlockTemplateForm(request.POST,instance = block_instance)
        if form.is_valid():
            block_instance = form.save(commit = False)
            if 'block' in request.POST:
                block_instance.block_id = request.POST['block']
                
            if 'facility_type' in request.POST:
                block_instance.facility_type = request.POST['facility_type']
                
            if 'time_period' in request.POST:
                block_instance.time_period = request.POST['time_period']

            block_instance.save()
            messages.success(request,"Successfully edited  Template Block")
        else:
            messages.warning(request,form.errors)

        return redirect('college:lp_block_template',pk=pk,period_pk=period_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_block_template_delete(request,pk,period_pk,block_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            c_instance = LearningProgrammeBlockTemplate.objects.get(id = block_pk)
            c_instance.delete()
            messages.success(request,"Successfully deleted Template Block")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:lp_block_template',pk=pk,period_pk=period_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    




    
class EducationPlanYearList(LoginRequiredMixin,ListView):
    template_name = 'college/education_plans.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(EducationPlanYearList, self).get(*args, **kwargs)

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








@login_required()
def education_plan_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        form = EducationPlanYearForm(request.POST)
        if form.is_valid():
            year_plan = form.save(commit = False)
            year_plan.cohort_registration_period_id = pk
            year_plan.save()

            messages.success(request,"Successfully added Year Plan")
        else:
            messages.warning(request,form.errors)

        return redirect('college:education_plans',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def education_plan_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        year_plan_instance = EducationPlanYear.objects.get(id = pk)
        period = year_plan_instance.cohort_registration_period
        form = EducationPlanYearForm(request.POST,instance = year_plan_instance)
        if form.is_valid():
            year_plan = form.save(commit = False)
            year_plan.save()
            messages.success(request,"Successfully edited Year Plan")
        else:
            messages.warning(request,form.errors)

        return redirect('college:education_plans',pk=period.id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def education_plan_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        c_instance = EducationPlanYear.objects.get(id = pk)
        period = c_instance.cohort_registration_period
        try:
            
            c_instance.delete()
            messages.success(request,"Successfully deleted Year")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:education_plans',pk=period.id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def education_plan_section_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        education_plan_year = EducationPlanYear.objects.get(id = pk)
        period = education_plan_year.cohort_registration_period
        form = EducationPlanYearSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit = False)
            section.education_plan_year = education_plan_year

            section.save()
            messages.success(request,"Successfully added Year Plan Section/Quarter")
        else:
            messages.warning(request,form.errors)

        return redirect('college:education_plans',pk=period.id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def education_plan_section_edit(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        section = EducationPlanYearSection.objects.get(id = pk)
        period = section.education_plan_year.cohort_registration_period

        form = EducationPlanYearSectionForm(request.POST,instance=section)
        if form.is_valid():
            form.save()
            messages.success(request,"Successfully edited Year Plan Section/Quarter")
        else:
            messages.warning(request,form.errors)

        return redirect('college:education_plans',pk=period.id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def education_plan_section_delete(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        section = EducationPlanYearSection.objects.get(id = pk)
        period = section.education_plan_year.cohort_registration_period

        try:
            section.delete()
            messages.success(request,"Successfully deleted Year Plan Section/Quarter")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:education_plans',pk=period)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def education_plan_weeks_create(request,pk):
    '''
    Function to create the weeks
    '''
    
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

    
        plan = EducationPlanYear.objects.get(id = pk)

        period = plan.cohort_registration_period
        
        EducationPlanYearSectionWeeks.objects.filter(education_plan_year_section__education_plan_year = plan).delete()
        
        sections = EducationPlanYearSection.objects.filter(education_plan_year = plan)
        
        academic_tracking = False
        
        academic_week_tracking = 0
        
        for week_num, start_date, end_date in sunday_year_weeks(plan.year):
            map_ = {'week':week_num,'date':f'{start_date} - {end_date}'}
            
            #we start first academic wwek in the second week
            if week_num == plan.academic_week_start:
                academic_tracking = True

            if academic_tracking:
                academic_week_tracking = academic_week_tracking + 1
                map_['academic'] = academic_week_tracking
                
            #check what section
            
            for section in sections:
               
                if start_date >= section.start_date and end_date <= section.end_date:
                    EducationPlanYearSectionWeeks.objects.create(
                        education_plan_year_section = section,
                        start_of_week = start_date,
                        end_of_week = end_date,
                        week_number = week_num,
                        academic_week_number = academic_week_tracking,
                    )
        
        messages.success(request,"Successfully created weeks")
        
        return redirect('college:education_plans',pk=period.id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
class EducationPlanYearSectionWeeksList(LoginRequiredMixin,ListView):
    template_name = 'college/education_plan_section_weeks.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(EducationPlanYearSectionWeeksList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  EducationPlanYearSectionWeeks.objects.filter(education_plan_year_section_id = self.kwargs['section_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['education_plan_menu'] = '--active'
        context['section'] = EducationPlanYearSection.objects.get(id = self.kwargs['section_pk'])
        plan = EducationPlanYear.objects.get(id = self.kwargs['pk'])
        period = plan.cohort_registration_period

        context['plan'] = plan
        context['period'] = period
        
        return context



class EducationPlanYearWeeksList(LoginRequiredMixin,ListView):
    template_name = 'college/education_plan_weeks.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(EducationPlanYearWeeksList, self).get(*args, **kwargs)

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


@login_required()
def education_plan_year_copy_template(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        period = cohort_period.period
        plan = cohort_period.education_plan

        master_plan = []

        master_plan_weeks = EducationPlanYearSectionWeeks.objects.filter(education_plan_year_section__education_plan_year = plan)

        for week in master_plan_weeks:
            academic_week_number = week.academic_week_number

            check_block_template_academic_week = period.block_template.filter(academic_week = academic_week_number)
            if check_block_template_academic_week.exists():
                block_template_academic_week = check_block_template_academic_week.first()
                week.facility_type = block_template_academic_week.facility_type
                week.time_period = block_template_academic_week.time_period
                week.block = block_template_academic_week.block
                week.save()

                    
        return redirect('college:education_plan_weeks',pk=plan.id)
          
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        


@login_required()
def education_plan_year_edit(request,pk,week_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        period = cohort_period.period
        plan = cohort_period.education_plan

        week_instance = EducationPlanYearSectionWeeks.objects.get(id = week_pk)
        form = EducationPlanYearSectionWeeksForm(request.POST,instance = week_instance)
        if form.is_valid():
            week = form.save(commit = False)
            if 'block' in request.POST:
                week.block_id = request.POST['block']
                
            if 'facility_type' in request.POST:
                week.facility_type = request.POST['facility_type']
                
            if 'time_period' in request.POST:
                week.time_period = request.POST['time_period']

            week.save()
            messages.success(request,"Successfully edited week")
        else:
            messages.warning(request,form.errors)

        return redirect('college:education_plan_weeks',pk=plan.id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def education_plan_year_delete(request,pk,week_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = pk)
        period = cohort_period.period
        plan = cohort_period.education_plan    
        
        try:
            week = EducationPlanYearSectionWeeks.objects.get(id = week_pk)
            week.delete()
            messages.success(request,"Successfully deleted")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:education_plan_weeks',pk=plan.id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


class EducationPlanYearSectionWilRequirementsList(LoginRequiredMixin,ListView):
    template_name = 'college/education_plan_section_wil_requirments.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(EducationPlanYearSectionWilRequirementsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  EducationPlanYearSectionWILRequirement.objects.filter(education_plan_year_section_id = self.kwargs['section_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['disciplines'] = Discipline.objects.all()
        context['education_plan_menu'] = '--active'
        section = EducationPlanYearSection.objects.get(id = self.kwargs['section_pk'])
        context['section'] = section
        plan = EducationPlanYear.objects.get(id = self.kwargs['pk'])
        period = plan.cohort_registration_period
        context['plan'] = plan
        context['period'] = period
        context['period_wil_requirements'] = LearningProgrammePeriodWILRequirement.objects.filter(period = period.period)
        return context

@login_required()
def education_plan_year_section_wil_requirement_add(request,pk,section_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        #check if the discipline exists in the section
        
        check_pline_exists = EducationPlanYearSectionWILRequirement.objects.filter(education_plan_year_section_id = section_pk,
                                                                                  period_wil_requirement_id = request.POST['period_wil_requirement']).exists()

        if check_pline_exists:
            messages.warning(request,'Sorry this discipline exists')
        else:
            #check if hours not used up
            wil_req = LearningProgrammePeriodWILRequirement.objects.get(id = request.POST['period_wil_requirement'])
            if wil_req.check_hour_balance_sections() > Decimal(request.POST['hours']):
                form = EducationPlanYearSectionWILRequirementForm(request.POST,request.FILES)
                if form.is_valid():
                    doc = form.save(commit=False)
                    doc.education_plan_year_section_id = section_pk
                    doc.period_wil_requirement_id = request.POST['period_wil_requirement']
                    doc.save()
                    messages.success(request,"Successfully added WIL Requirement to section")
                else:
                    messages.warning(request,form.errors)
            else:
                messages.warning(request,f'Hours allocated are higher than the hours left to allocate: {wil_req.check_hour_balance_sections()}')

        return redirect('college:education_plan_year_section_wil_requirements',pk=pk,section_pk=section_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def education_plan_year_section_wil_requirement_edit(request,pk,section_pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        doc = EducationPlanYearSectionWILRequirement.objects.get(id = wil_pk)
        form = EducationPlanYearSectionWILRequirementForm(request.POST,instance = doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()

            messages.success(request,"Successfully edited WIL Requirement")
        else:
            messages.warning(request,form.errors)

        return redirect('college:education_plan_year_section_wil_requirements',pk=pk,section_pk=section_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
@login_required()
def education_plan_year_section_wil_requirement_delete(request,pk,section_pk,wil_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1:

        try:
            lp = EducationPlanYearSectionWILRequirement.objects.get(id = wil_pk)
            lp.delete()
            messages.success(request,"Successfully deleted WIL Requirement")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:education_plan_year_section_wil_requirements',pk=pk,section_pk=section_pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class LearningProgrammeCohortPeriodEducationList(LoginRequiredMixin,ListView):
    template_name = 'college/learning_programme_cohorts_education_master_plan.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortPeriodEducationList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CohortRegistrationPeriodEducationPlan.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        context['cohort_menu'] = '--active'
        context['period'] = period
        context['cohort'] = period.learning_programme_cohort
        context['learning_programme'] = period.learning_programme_cohort.learning_programme
        context['blocks'] = ProgarmmeBlock.objects.all()
        
        return context
    


@login_required()
def learning_programme_cohort_education_plan_add(request,pk,period_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        #check academic week exists
        
        check_week_exists = LearningProgrammeBlockTemplate.objects.filter(period_id = period_pk,academic_week=request.POST['academic_week']).exists()

        if check_week_exists:
            messages.warning(request,'You cannot have a duplicate academic week')
        else:
            form = LearningProgrammeCohortRegistrationPeriodEducationPlanForm(request.POST)
            if form.is_valid():
                block_instance = form.save(commit = False)
                block_instance.cohort_registration_period_id = pk
                if 'block' in request.POST:
                    block_instance.block_id = request.POST['block']
                    
                if 'facility_type' in request.POST:
                    block_instance.facility_type = request.POST['facility_type']
                    
                if 'time_period' in request.POST:
                    block_instance.time_period = request.POST['time_period']

                block_instance.save()

                messages.success(request,"Successfully added Block")
            else:
                messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_education_plan',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def print_education_plan(request,pk):
   
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        mapsterplan_print = MyPrintMasterPlan(f'{pk}.pdf', 'A4')
        filename = mapsterplan_print.print_masterplan(pk)

        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response

        raise Http404
       
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



'''
Timetable Days Master Plan
'''


@login_required()
def view_education_plan_days(request,pk):
    
    '''
    days of the week
    '''
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2):

        week = EducationPlanYearSectionWeeks.objects.get(id = pk)
        
        #check if days exist , if not add them
        if week.days.count() == 0:
            # Generate a list of days between start_date and end_date
            days_in_week = [(week.start_of_week + datetime.timedelta(days=i)) for i in range(7)]
            for day in days_in_week:
                EducationPlanYearSectionWeekDay.objects.create(
                    education_plan_section_week = week,
                    day = day,
                )
                
        period = week.education_plan_year_section.education_plan_year.cohort_registration_period
        learning_programme = period.learning_programme_cohort.learning_programme
        modules = period.modules.all()
        procedures = period.cohort_period_procedures.all()
        learning_programme_period = period.period
        sessions = learning_programme_period.timetable_sessions.all()
        staffs = Staff.objects.all()
        
        return render(request,'college/education_plan_days.html',{'procedures':procedures,
                                                                  'modules':modules,
                                                                  'learning_programme':learning_programme,
                                                                  'period':period,
                                                                  'cohort_menu':'--active',
                                                                  'week':week,
                                                                  'staffs':staffs,
                                                                  'sessions':sessions})
            
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def save_education_plan_day_session(request,pk):
    
    '''
    save session
    '''
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2):

        day = EducationPlanYearSectionWeekDay.objects.get(id = pk)
        week = day.education_plan_section_week
        #cehck if session exists
        check_session = EducationPlanYearSectionWeekDaySession.objects.filter(session_id = request.POST['session'],day=day).exists()
        if not check_session:
            session = EducationPlanYearSectionWeekDaySession.objects.create(day = day,
                                                                            session_id = request.POST['session'])
            
            if 'credits' in request.POST:
                session.credits = request.POST['credits']
            
            if week.block.block_name == 'Theory Block':

                if 'module' in request.POST:
                    session.module_id = request.POST['module']
        
                if 'study_unit' in request.POST:
                    session.study_unit_id = request.POST['study_unit']

                session.save()
                
            elif week.block.block_name == 'Simulation':
                
                if 'type_procedure' in request.POST:
                    session.type_procedure = request.POST['type_procedure']
                    
                procedure_ids = request.POST.getlist('procedures[]')
                
                for p_id in procedure_ids:
                    procedure = CohortRegistrationProcedure.objects.get(id = p_id)
                    session.procedures.add(procedure)
                    
                session.save()
                
            staffs = request.POST.getlist('staff_selected[]')
            print(staffs)
            for s_id in staffs:
                staff = Staff.objects.get(id = s_id)
                session.lecturers.add(staff)
                session.save()
                print('innnnn')

            messages.success(request,'Successfully added Session')
            
        else:
            messages.warning(request,'Session already exists')
                
        return redirect('college:view_education_plan_days',pk=week.id)            
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def edit_education_plan_day_session(request,pk,session_pk):
    '''
    edit session
    '''
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2):

        session = EducationPlanYearSectionWeekDaySession.objects.get(id = session_pk)
        day = EducationPlanYearSectionWeekDay.objects.get(id = pk)
        week = day.education_plan_section_week
        
        check_session = EducationPlanYearSectionWeekDaySession.objects.filter(session_id = request.POST['session'],day=day).exists()
        if not check_session:
            session.session_id = request.POST['session']
            
        if 'credits' in request.POST:
            session.credits = request.POST['credits']
        
        if week.block.block_name == 'Theory Block':

            if 'module' in request.POST:
                session.module_id = request.POST['module']
    
            if 'study_unit' in request.POST:
                session.study_unit_id = request.POST['study_unit']

            session.save()
            
        elif week.block.block_name == 'Simulation':
            
            if 'type_procedure' in request.POST:
                session.type_procedure = request.POST['type_procedure']
                
            procedure_ids = request.POST.getlist('procedures[]')
            session.procedures.clear()
            for p_id in procedure_ids:
                procedure = CohortRegistrationProcedure.objects.get(id = p_id)
                session.procedures.add(procedure)
                
            session.save()
            
        staffs = request.POST.getlist('staff_selected[]')
        session.lecturers.clear()
        for s_id in staffs:
            staff = Staff.objects.get(id = s_id)
            session.lecturers.add(staff)
            session.save()

        messages.success(request,'Successfully edited Session')
        
        
        return redirect('college:view_education_plan_days',pk=week.id)            
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def delete_education_plan_day_session(request,pk,session_pk):
    
    '''
    delete session
    '''
    
    if (request.user.logged_in_role_id == 6 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2):

        session = EducationPlanYearSectionWeekDaySession.objects.get(id = session_pk)
        day = EducationPlanYearSectionWeekDay.objects.get(id = pk)
        week = day.education_plan_section_week
        #cehck if session exists
        try:
            session.delete()
            messages.success(request,'Successfully deleted Session')
            
        except Exception as e:
            messages.warning(request,f'An error has Occured: {str(e)}')
                
        return redirect('college:view_education_plan_days',pk=week.id)            
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def print_education_plan_week(request,pk):
   
    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        mapsterplan_print_week = MyPrintMasterPlanWeek(f'{pk}.pdf', 'A4')
        filename = mapsterplan_print_week.print_masterplan_days(pk)

        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response

        raise Http404
       
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

class LearningProgrammeCohortRegistrationAttendanceRegisterList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_period_registers.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationAttendanceRegisterList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  StudentLearningProgrammeRegistrationRegister.objects.filter(cohort_registration_period__id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['students'] = learning_programme_cohort_registration_period.registrations.all()
        context['categories'] = RegisterCategory.objects.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        return context

@login_required()
def learning_programme_cohort_registration_attendance_register_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:
        
        form = StudentLearningProgrammeRegistrationRegisterForm(request.POST)
        if form.is_valid():
            register = form.save(commit=False)
            register.cohort_registration_period_id = pk
            register.user = request.user
            if 'category' in request.POST:
                register.category_id = request.POST['category']

            register.save()

            students = request.POST.getlist('students[]')

            for student_pk in students:
                reg = StudentLearningProgrammeRegistration.objects.get(id = student_pk)
                register.students.add(reg)

            messages.success(request,"Successfully added attendance register")
        else:
            messages.warning(request,form.errors)
            
        return redirect('college:learning_programme_cohort_registration_attendance_registers',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_attendance_register_edit(request,pk,register_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        register = StudentLearningProgrammeRegistrationRegister.objects.get(id = register_pk)
        form = StudentLearningProgrammeRegistrationRegisterForm(request.POST,instance = register)
        if form.is_valid():
            register = form.save(commit=False)
            if 'category' in request.POST:
                register.category_id = request.POST['category']
            register.save()

            messages.success(request,"Successfully edited attendnace register")
        else:
            messages.warning(request,form.errors)

        return redirect('college:learning_programme_cohort_registration_attendance_registers',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def learning_programme_cohort_registration_attendance_register_delete(request,pk,register_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            procedure = StudentLearningProgrammeRegistrationRegister.objects.get(id = register_pk)
            procedure.delete()
            messages.success(request,"Successfully deleted attendance register")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_attendance_registers',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


class LearningProgrammeCohortRegistrationAttendanceRegisterStudentList(LoginRequiredMixin,ListView):
    template_name = 'college/learing_programme_cohort_registration_period_register_students.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(LearningProgrammeCohortRegistrationAttendanceRegisterStudentList, self).get(*args, **kwargs)

    def get_queryset(self):
        register =  StudentLearningProgrammeRegistrationRegister.objects.get(id = self.kwargs['pk'])
        return register.students.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        register = StudentLearningProgrammeRegistrationRegister.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort_registration_period = register.cohort_registration_period
        learning_programme_cohort = learning_programme_cohort_registration_period.learning_programme_cohort 
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme_cohort.learning_programme
        context['students'] = learning_programme_cohort_registration_period.registrations.all()
        context['cohort_menu'] = '--active'
        context['learning_programme_cohort_registration_period'] = learning_programme_cohort_registration_period
        context['register'] = register
        return context



@login_required()
def learning_programme_cohort_registration_attendance_register_student_add(request,pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        students = request.POST.getlist('students[]')

        register = StudentLearningProgrammeRegistrationRegister.objects.get(id = pk)

        for student_pk in students:
            reg = StudentLearningProgrammeRegistration.objects.get(id = student_pk)
            register.students.add(reg)

        return redirect('college:learning_programme_cohort_registration_attendance_register_students',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def learning_programme_cohort_registration_attendance_register_student_delete(request,pk,student_pk):

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        try:
            register = StudentLearningProgrammeRegistrationRegister.objects.get(id = pk)
            student = StudentLearningProgrammeRegistration.objects.get(id = student_pk)
            register.students.remove(student)
            register.save()
            
            messages.success(request,"Successfully removed student")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('college:learning_programme_cohort_registration_attendance_register_students',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

    
@login_required()
def ajax_fetch_facility_discipline_wards(request,pk):
    
    
    try:
        registration = StudentLearningProgrammeRegistration.objects.get(id = pk)
        
       #facility = 

        if discipline_check.exists():
            discipline = discipline_check.first()
          
            
            info = []
            if discipline.wards.count() > 0:
                for x in discipline.wards.all():
                    info.append({'id':x.id,'ward':x.ward})
                    
                data = {
                    'valid':1,
                    'discipline_id':discipline.id,
                }
                data['info'] = info
            else:
                data = {
                    'valid':0,
                    'message':'No wards'
                }    
        else:
            data = {
                'valid':0,
                'message':'No wards'
            }
    except Exception as e:
        data = {
            'valid':2,
            'message':'str(e)'
        }

    return JsonResponse(data)


@login_required()
def ajax_fetch_facility_ward_disciplines(request):
    
    
    try:
        ward_id = request.GET.get('ward_id', None)
        
        facility_ward = HealthCareFacilityWard.objects.get(id = ward_id)
                
        disciplines = facility_ward.ward.disciplines.all()
                
        info = []
        
        if disciplines.count() > 0:
            for x in disciplines:
                info.append({'id':x.id,'discipline':x.discipline})
                
            data = {
                'valid':1,
                'ward_id':facility_ward.id,
            }
            data['info'] = info
        else:
            data = {
                'valid':0,
                'message':'No Disciplines'
            }    
        
    except Exception as e:
        data = {
            'valid':2,
            'message':'str(e)'
        }

    return JsonResponse(data)



def ajax_fetch_study_units(request):
    module_id = request.GET.get('module_id', None)
    try:
        module_check = CohortRegistrationPeriodModule.objects.filter(id = module_id)

        if module_check.exists():
            module = module_check.first()
            data = {
                'valid':1,
                'module_id':module.id,
            }
            info = []
            for s in module.module.study_units.all():
                info.append({'id':s.id,'text':f'{s.study_unit_code}: {s.study_unit_name}'})

            data['info'] = info
        else:
            data = {
                'valid':0,
                'message':'No Study Units'
            }
    except Exception as e:
        data = {
            'valid':2,
            'message':'str(e)'
        }

    return JsonResponse(data)