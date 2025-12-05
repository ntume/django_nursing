from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date
import datetime

from college.models import LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod

from .models import Announcement, AnnouncementCategory, LearningProgrammeCohortAnnouncement, LearningProgrammeCohortRegisteredAnnouncement
from .forms import AnnouncementForm, AnnouncementCategoryForm, LearningProgrammeCohortAnnouncementForm, LearningProgrammeCohortRegisteredAnnouncementForm
from accounts.models import Role, User


class AnnouncementCategoryListView(LoginRequiredMixin,ListView):
    template_name = 'announcements/announcement_category_list.html'
    model = AnnouncementCategory
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AnnouncementCategoryForm()
        context['form'] = form
        context['config_menu'] = '--active'
        context['config_menu_open'] = 'side-menu__sub-open'
        context['announcement_category_menu_open'] = '--active'
        return context

@login_required()
def add_announcement_category(request):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        form = AnnouncementCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Announcement category added successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('announcements:config_announcement_categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_announcement_category(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
       
        category_instance = AnnouncementCategory.objects.get(id = pk)

        form = AnnouncementCategoryForm(request.POST,instance = category_instance)
        if form.is_valid():
            form.save()
            messages.success(request,'Category edited successfully')
        else:
            messages.warning(request,form.errors)

          
        return redirect('announcements:config_announcement_categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def delete_announcement_category(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        category_instance = AnnouncementCategory.objects.get(id = pk)
        try:
            category_instance.delete()
            messages.success(request,'Category deleted successfully')
        except Exception as e:
            messages.warning(request,str(e))

        return redirect('announcements:config_announcement_categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



class AnnouncementListView(LoginRequiredMixin,ListView):
    template_name = 'announcements/announcements.html'
    model = Announcement
    context_object_name = 'announcements'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = AnnouncementCategory.objects.all()
        context['announcement_menu_open'] = '--active'
        context['roles'] = Role.objects.all()
        return context

@login_required()
def add_announcement(request):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            if 'category' in request.POST:
                announcement.category_id = request.POST['category']
            if 'role' in request.POST:
                announcement.role_id = request.POST['role']
            announcement.user = request.user
            announcement.save()
            messages.success(request,'Announcement added successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('announcements:announcement_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_announcement(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
       
        announcement_instance = Announcement.objects.get(id = pk)

        form = AnnouncementForm(request.POST,instance = announcement_instance)
        if form.is_valid():
            announcement = form.save(commit=False)
            if 'category' in request.POST:
                announcement.category_id = request.POST['category']
            if 'role' in request.POST:
                announcement.role_id = request.POST['role']
            announcement.save()
            messages.success(request,'Announcement edited successfully')
        else:
            messages.warning(request,form.errors)

          
        return redirect('announcements:announcement_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def delete_announcement(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        announcement = Announcement.objects.get(id = pk)
        try:
            announcement.delete()
            messages.success(request,'Announcement deleted successfully')
        except Exception as e:
            messages.warning(request,str(e))

        return redirect('announcements:announcement_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class CohortAnnouncementListView(LoginRequiredMixin,ListView):
    template_name = 'announcements/cohort_announcements.html'
    context_object_name = 'announcements'

    
    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CohortAnnouncementListView, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCohortAnnouncement.objects.filter(learning_programme_cohort_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = self.kwargs['pk'])
        learning_programme = learning_programme_cohort.learning_programme

        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['categories'] = AnnouncementCategory.objects.all()
        context['cohort_menu'] = '--active'
        context['roles'] = Role.objects.all()
        return context

@login_required()
def add_cohort_announcement(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        form = LearningProgrammeCohortAnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            if 'category' in request.POST:
                announcement.category_id = request.POST['category']
            if 'role' in request.POST:
                announcement.role_id = request.POST['role']

            announcement.learning_programme_cohort_id = pk
            announcement.user = request.user
            announcement.save()
            messages.success(request,'Announcement added successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('announcements:cohort_announcement_list',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_cohort_announcement(request,pk,announcement_pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
       
        announcement_instance = LearningProgrammeCohortAnnouncement.objects.get(id = announcement_pk)

        form = LearningProgrammeCohortAnnouncementForm(request.POST,instance = announcement_instance)
        if form.is_valid():
            announcement = form.save(commit=False)
            if 'category' in request.POST:
                announcement.category_id = request.POST['category']
            if 'role' in request.POST:
                announcement.role_id = request.POST['role']
            announcement.save()
            messages.success(request,'Announcement edited successfully')
        else:
            messages.warning(request,form.errors)

          
        return redirect('announcements:cohort_announcement_list',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def delete_cohort_announcement(request,pk,announcement_pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        announcement = LearningProgrammeCohortAnnouncement.objects.get(id = announcement_pk)
        try:
            announcement.delete()
            messages.success(request,'Announcement deleted successfully')
        except Exception as e:
            messages.warning(request,str(e))

        return redirect('announcements:cohort_announcement_list',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class CohortRegistrationAnnouncementListView(LoginRequiredMixin,ListView):
    template_name = 'announcements/cohort_registration_announcements.html'
    context_object_name = 'announcements'

    
    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 2 and self.request.user.logged_in_role_id != 1 and self.request.user.logged_in_role_id != 6:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CohortRegistrationAnnouncementListView, self).get(*args, **kwargs)

    def get_queryset(self):
        return  LearningProgrammeCohortRegisteredAnnouncement.objects.filter(learning_programme_cohort_registration_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_programme_cohort_registration = LearningProgrammeCohortRegistrationPeriod.objects.get(id = self.kwargs['pk'])
        learning_programme_cohort = learning_programme_cohort_registration.learning_programme_cohort
        learning_programme = learning_programme_cohort.learning_programme

        context['learning_programme_cohort_registration'] = learning_programme_cohort_registration
        context['learning_programme_cohort'] = learning_programme_cohort
        context['learning_programme'] = learning_programme
        context['categories'] = AnnouncementCategory.objects.all()
        context['cohort_menu'] = '--active'
        context['roles'] = Role.objects.all()
        return context

@login_required()
def add_cohort_registration_announcement(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:
        form = LearningProgrammeCohortRegisteredAnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            if 'category' in request.POST:
                announcement.category_id = request.POST['category']
            if 'role' in request.POST:
                announcement.role_id = request.POST['role']

            announcement.learning_programme_cohort_registration_id = pk
            announcement.user = request.user
            announcement.save()
            messages.success(request,'Announcement added successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('announcements:cohort_registration_announcement_list',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_cohort_registration_announcement(request,pk,announcement_pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:
       
        announcement_instance = LearningProgrammeCohortRegisteredAnnouncement.objects.get(id = announcement_pk)

        form = LearningProgrammeCohortRegisteredAnnouncementForm(request.POST,instance = announcement_instance)
        if form.is_valid():
            announcement = form.save(commit=False)
            if 'category' in request.POST:
                announcement.category_id = request.POST['category']
            if 'role' in request.POST:
                announcement.role_id = request.POST['role']
            announcement.save()
            messages.success(request,'Announcement edited successfully')
        else:
            messages.warning(request,form.errors)

          
        return redirect('announcements:cohort_registration_announcement_list',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def delete_cohort_registration_announcement(request,pk,announcement_pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 6:
        announcement = LearningProgrammeCohortRegisteredAnnouncement.objects.get(id = announcement_pk)
        try:
            announcement.delete()
            messages.success(request,'Announcement deleted successfully')
        except Exception as e:
            messages.warning(request,str(e))

        return redirect('announcements:cohort_registration_announcement_list',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')