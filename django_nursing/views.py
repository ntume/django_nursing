from django.views.generic import TemplateView,ListView
from blog.models import Blog,Comment
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.defaults import page_not_found
from events.models import EventCompanyRSVP
import datetime

def handler404(request, exception=404):
    return render(request, '404.html', status=404)

def handler500(request, exception=500):
    return render(request, '500.html', status=500)

class HomePage(ListView):
    template_name = 'intro_page.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Blog.objects.filter(viewership__exact = 'Public', publish__exact='Yes').order_by('created_at')

def home_page(request):

    if request.user.is_authenticated:

        if request.user.logged_in_role_id == 1:
            messages.success(request,'Successfully logged in')
            return redirect('administration:dashboard_principal')

        elif request.user.logged_in_role_id == 2:
            messages.success(request,'Successfully logged in')
            return redirect('/administration/')
        
        elif request.user.logged_in_role_id == 3:
            messages.success(request,'Successfully logged in')
            return redirect('administration:dashboard_librarian')
        
        elif request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
            messages.success(request,'Successfully logged in')
            return redirect('administration:dashboard_lecturer')
        
        elif request.user.logged_in_role_id == 6:
            messages.success(request,'Successfully logged in')
            return redirect('administration:dashboard_programme_coordinator')

        elif request.user.logged_in_role_id == 10:
            messages.success(request,'Successfully logged in')
            return redirect('students:student_dashboard')
        
        elif request.user.logged_in_role_id == 11:
            messages.success(request,'Successfully logged in')
            return redirect('college:facility_hod_dashboard')
        
        elif request.user.logged_in_role_id == 12:
            messages.success(request,'Successfully logged in')
            return redirect('college:co_assessor_dashboard')

    else:
        
        return redirect('accounts:login_user')

def privacy(request):

    return render(request,'privacy-policy.html')