from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


# Create your views here.
@login_required()
def dashboard(request):

    return render(request,'administration/dashboard.html',{'dash_menu':'--active'})

@login_required()
def dashboard_librarian(request):

    return render(request,'administration/dashboard.html',{'dash_menu':'--active'})


@login_required()
def dashboard_lecturer(request):

    return render(request,'administration/dashboard.html',{'dash_menu':'--active'})


@login_required()
def dashboard_principal(request):

    return render(request,'administration/dashboard.html',{'dash_menu':'--active'})


@login_required()
def dashboard_programme_coordinator(request):

    return render(request,'administration/dashboard.html',{'dash_menu':'--active'})




