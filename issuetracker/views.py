from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib import messages

from .models import IssueTracker,IssueTrackerComments
from .forms import IssueTrackerCommentsForm,IssueTrackerForm
from accounts.models import User

# Create your views here.
class IssueTrackerList(LoginRequiredMixin,ListView):
    template_name = 'issuetracker/issuetracker_list.html'
    model = IssueTracker
    context_object_name = 'issues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = IssueTrackerForm()
        context['form'] = form
        context['config_menu'] = 'active'
        return context

@login_required()
def add_issuetracker(request):
    if request.method == 'POST':
        form = IssueTrackerForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user
            issue.save()
            messages.success(request,'Successfully added Issue Tracker Entry')
        else:
            messages.warning(request,form.errors)

    if request.user.roles_id == 2:
        return redirect('wil:config_issuetracker')
    elif request.user.roles_id == 10:
        return redirect('psycad:config_issuetracker')
    else:
        return redirect('accounts:logout')



@login_required()
def edit_issuetracker(request,pk):
    if request.method == 'POST':
        try:
            issue_instance = IssueTracker.objects.get(id = pk)
            if request.POST['task'] == 'delete':
                issue_instance.delete()
                messages.success(request,'Successfully deleted issue tracker entry')
            elif request.POST['task'] == 'edit':
                form = IssueTrackerForm(request.POST,instance=issue_instance)
                if form.is_valid():
                    form.save()
                    messages.success(request,'Successfully edited issue tracker entry')
                else:
                    messages.warning(request,form.errors)
        except:
            messages.warning(request,e.message)

    if request.user.roles_id == 2:
        return redirect('wil:config_issuetracker')
    elif request.user.roles_id == 10:
        return redirect('psycad:config_issuetracker')
    else:
        return redirect('accounts:logout')

@login_required()
def add_issuetrackercomment(request,pk):
    issue_instance = IssueTracker.objects.get(id = pk)
    form = IssueTrackerCommentsForm(request.POST)
    if form.is_valid():
        comment = form.save(commit = False)
        comment.user = request.user
        comment.issuetracker = issue_instance
        comment.save()
        messages.success(request,'Successfully added comment')
    else:
        messages.warning(request,form.errors)

    if request.user.roles_id == 2:
        return redirect('wil:config_issuetracker')
    elif request.user.roles_id == 10:
        return redirect('psycad:config_issuetracker')
    else:
        return redirect('accounts:logout')
