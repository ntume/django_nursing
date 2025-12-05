from django.urls import path
from . import views
from configurable.views import *
from college.views import *

app_name = 'administration'

urlpatterns = [    
    path('',views.dashboard,name='dashboard'),
    path('librarian',views.dashboard_librarian,name='dashboard_librarian'),
    path('lecturer',views.dashboard_lecturer,name='dashboard_lecturer'),
    path('principal',views.dashboard_principal,name='dashboard_principal'),
    path('coordinator',views.dashboard_programme_coordinator,name='dashboard_programme_coordinator'),
]
