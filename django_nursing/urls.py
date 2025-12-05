"""uj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from . import views
from todo.views import add_task_ajax, update_task_status

urlpatterns = [
    path('404/', views.handler404),
    path('admin/', admin.site.urls),
    path('',views.home_page,name='blog-list'),
    path('todo/add/ajax',add_task_ajax,name='add_task_ajax'),
    path('todo/update',update_task_status,name='update_task_status'),
    path('administration/',include('administration.urls',namespace='administration')),
    path('accounts/',include('accounts.urls',namespace='accounts')),
    path('students/',include('students.urls',namespace='students')),
    path('events/',include('events.urls',namespace='events')),
    path('adverts/',include('adverts.urls',namespace='adverts')),
    path('college/',include('college.urls',namespace='college')),
    path('blog/', include('blog.urls',namespace='blog')),
    path('configurable/', include('configurable.urls',namespace='configurable')),
    path('api/', include('api.urls',namespace='api')),
    path('appointments/', include('appointments.urls',namespace='appointments')),
    path('library/', include('libraryms.urls',namespace='library')),
    path('announcements/', include('announcements.urls',namespace='announcements')),
    path('privacy/',views.privacy,name='privacy'),
    path('facility/management',include('facility_management.urls',namespace='facilities')),
    path('resource/management',include('resource_management.urls',namespace='resources')),
    path('__debug__/', include('debug_toolbar.urls')),
]

if settings.DEBUG: # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'django_nursing.views.handler404'
handler500 = 'django_nursing.views.handler500'
