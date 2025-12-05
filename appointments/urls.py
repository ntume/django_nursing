from django.urls import path

from appointments.print_appointment_report import print_appointment_list_excel
from students.views_student import student_dashboard
from . import views

app_name = 'appointments'

urlpatterns = [
    path('config/appointment/category/',views.AppointmentCategoryListView.as_view(),name='config_appointment_categories'),
    path('config/appointment/category/add',views.add_appointment_category,name='add_appointment_category'),
    path('config/appointment/category/<int:pk>/edit/',views.edit_appointment_category,name='edit_appointment_category'),
    path('config/appointment/category/<int:pk>/delete/',views.delete_appointment_category,name='delete_appointment_category'),
    path('config/appointment/contact/method/',views.AppointmentContactListView.as_view(),name='config_appointment_contact_methods'),
    path('config/appointment/contact/method/add',views.add_appointment_contact_method,name='add_appointment_contact_method'),
    path('config/appointment/contact/method/<int:pk>/edit',views.edit_appointment_contact_method,name='edit_appointment_contact_method'),
    path('config/appointment/contact/method/<int:pk>/delete',views.delete_appointment_contact_method,name='delete_appointment_contact_method'),
    
    path('config/appointment/recommendation/',views.AppointmentRecommendationListView.as_view(),name='config_appointment_recommendations'),
    path('config/appointment/recommendation/add',views.add_appointment_recommendation,name='add_appointment_recommendation'),
    path('config/appointment/recommendation/<int:pk>/edit',views.edit_appointment_recommendation,name='edit_appointment_recommendation'),
    path('config/appointment/recommendation/<int:pk>/delete',views.delete_appointment_recommendation,name='delete_appointment_recommendation'),
    
    path('staff/my/appointments/',views.appointments_my_list,name='appointments_my_list'),
    path('staff/my/appointments/filter',views.appointments_my_list_filter,name='appointments_my_list_filter'),
    path('staff/my/appointments/<int:pk>/remove',views.appointment_remove,name='appointment_remove'),
    path('staff/my/appointments/<int:pk>/edit',views.appointment_edit_status,name='appointment_edit_status'),
    path('staff/my/appointments/<int:pk>/add/note',views.appointment_add_notes,name='appointment_add_notes'),
    path('staff/my/appointments/remove/note/<int:pk>',views.appointment_delete_notes,name='appointment_delete_notes'),

    path('principal/all/appointments/',views.AllAppointmentsList.as_view(),name='appointments_all_list'),
    path('principal/all/appointments/filter',views.appointments_all_list_filter,name='appointments_all_list_filter'),
    
    path('student/appointments/',views.appointment_student_list,name='appointment_student_list'),
    path('student/appointments/request',views.request_appointment,name='request_appointment'),
    path('student/appointments/<int:pk>/edit',views.edit_appointment,name='edit_appointment'),
    path('student/appointments/<int:pk>/capture/feedback',views.appointment_feedback,name='appointment_feedback'),
    
    path('student/appointments/<int:pk>/new/time/accepted',views.appointment_new_time_accept,name='appointment_new_time_accept'),    
    path('student/appointments/<int:pk>/new/time/rejected',views.appointment_new_time_reject,name='appointment_new_time_reject'),
    
    path('report/appointments/',views.appointments_report_list,name='appointments_report_list'),
    path('report/appointments/filter',views.appointments_report_list_filter,name='appointments_report_list_filter'),
    path('report/appointments/export/<str:filterstr>/excel',print_appointment_list_excel,name='print_appointment_list_excel'),    
    path('report/appointments/export/<str:filterstr>/pdf',views.create_appointment_report_pdf,name='create_appointment_report_pdf'), 
    
]