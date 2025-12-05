from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import ListView

from .models import Task
from accounts.models import User

# Create your views here.

class TaskListView(LoginRequiredMixin,ListView):
    template_name = 'task.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(user = self.request.user,status__exact = 'Pending')

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['task_menu'] = 'active'
        return context

@login_required()
def task_list(request):
    return task.objects.filter(user=request.user)

@login_required()
def update_task_status(request):
    status = request.GET.get('status', None)
    pk = request.GET.get('pk', None)

    task = Task.objects.get(id=pk)

    print('in')

    try:
        task.status = status
        task.save()
        data = { 'is_successful': True,'id':task.id }
    except:
        data = { 'is_successful': False }

    print(data)
    return JsonResponse(data)

@login_required()
def add_task_ajax(request):
    task = request.GET.get('task', None)
    try:
        task = Task(task=task,user=request.user)
        task.save()
        data = { 'is_successful': True,'id':task.id }
    except:
        data = { 'is_successful': False }

    #json_data = json.dumps(request.POST)
    #return HttpResponse(json_data, content_type='application/json')
    return JsonResponse(data)

@login_required()
def add_task(request):
    task = Task(task=request.POST['task'],user=request.user)
    task.save()

    if request.user.roles_id == 10:
        return redirect('psycad:list_tasks')
    elif request.user.roles_id == 2:
        return redirect('wil:list_tasks')
