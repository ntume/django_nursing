from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from .models import Funder, Funding, FundingRep, FundingStudent
from .forms import FunderForm, FundingForm
from faculties.models import Lecturer

# Create your views here.

class FundingListView(LoginRequiredMixin,ListView):
    template_name = 'funder/funding.html'
    context_object_name = 'funding'
    model = Funding

    def get_queryset(self):
        LecturerUser = get_object_or_404(Lecturer,user_id = self.request.user.id)        
        return Funding.objects.filter(funder_id = self.kwargs['pk'],faculty = LecturerUser.department.faculty).order_by('-start')

    def get_context_data(self, **kwargs):
        context = super(FundingListView, self).get_context_data(**kwargs)
        funder = Funder.objects.get(id=self.kwargs['pk'])
        context['funder'] = funder
        context['fund_menu'] = 'active'
        return context


@login_required()
def addfunding(request,pk):

    try:
        LecturerUser = Lecturer.objects.get(user_id = request.user.id)
    except:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

    form = FundingForm(request.POST)
    if form.is_valid():
        funding = form.save(commit=False)
        funding.faculty = LecturerUser.department.faculty
        funding.funder_id = pk
        funding.save()
        messages.success(request,'Successfully added funding')
    else:
        messages.warning(request,form.errors)

    return redirect('wil:funding',pk=pk)


@login_required()
def editfunding(request,funder_pk,pk):
    #LecturerUser = Lecturer.objects.get(user_id = request.user.id)
    try:
        funding = Funding.objects.get(id=pk)
        form = FundingForm(request.POST,instance=funding)
        if form.is_valid():
            form.save()
            messages.success(request,'Successfully edited funding')
        else:
            messages.warning(request,form.errors)
    except:
        messages.warning(request,'Funding does not exist')

    return redirect('wil:funding',pk=funder_pk)


@login_required()
def deletefunding(request,funder_pk,pk):
    try:
        funding = Funding.objects.get(id=pk)
        funding.delete()
        messages.success(request,'Successfully deleted funding')
    except:
        messages.warning(request,'An error occured, please try again')

    return redirect('wil:funding',pk=funder_pk)


class FundingStudentListView(LoginRequiredMixin,ListView):
    template_name = 'funder/funding_students.html'
    context_object_name = 'funding'
    model = Funding

    def get_queryset(self):
        return Funding.objects.get(id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(FundingStudentListView, self).get_context_data(**kwargs)
        context['fund_menu'] = 'active'
        return context

@login_required()
def deletefundingstudent(request,funder_pk,funding_pk,pk):
    try:
        student = FundingStudent.objects.get(id=pk)
        student.delete()
        messages.success(request,'Successfully removed student from funding')
    except:
        messages.warning(request,'An error occurred, please try again pr contact your administrator')

    return redirect('wil:funding_students',funder_pk,funding_pk)
