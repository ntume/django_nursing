from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('',views.EventList.as_view(),name='eventlist'),
    path('rsvp/',views.EventRSVPList.as_view(),name='eventrsvp'),
    path('addrsvp/<int:pk>/',views.event_add_rsvp,name='addrsvp'),
    path('removersvp/<int:pk>/',views.remove_rsvp,name='removersvp'),
    path('ajax/fetch/forms/',views.ajax_fetch_reg_forms,name='ajax_fetch_reg_forms'),
    path('ajax/fetch/event/',views.ajax_fetch_event_info,name='ajax_fetch_event_info'),
]
