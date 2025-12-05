from django.urls import path

from resource_management.print_resource_report import print_resource_list_excel
from . import views

app_name = 'resources'

urlpatterns = [
            
    path('admin/resources/',views.ResourceList.as_view(),name='resources'),
    path('admin/resource/add',views.add_resource,name='add_resource'),
    path('admin/resource/<int:pk>/edit',views.edit_resource,name='edit_resource'),   
    path('admin/resource/<int:pk>/delete',views.delete_resource,name='delete_resource'),   

    path('admin/resource/<int:pk>/admins/add',views.add_resource_administrators,name='add_resource_administrators'), 
    path('admin/resource/<int:pk>/admins/<int:admin_pk>/remove',views.remove_resource_administrator,name='remove_resource_administrator'),

    path('admin/resource/bookings',views.ResourceAdminBookingsList.as_view(),name='resource_bookings'),
    path('admin/resource/bookings/filter',views.resource_bookings_filter,name='resource_bookings_filter'),
    path('admin/resource/booking/<int:pk>/approve',views.approve_student_resource_booking,name='approve_student_resource_booking'),
    
    path('staff/resource/bookings',views.resource_booking_staff_list,name='resource_booking_staff_list'),
    path('staff/resource/booking/request/',views.staff_request_resource_booking,name='staff_request_resource_booking'),
    path('staff/resource/booking/<int:pk>/edit',views.edit_staff_resource_booking,name='edit_staff_resource_booking'),

    path('student/bookings/',views.resource_booking_student_list,name='resource_booking_student_list'),
    path('student/bookings/request',views.student_request_resource_booking,name='student_request_resource_booking'),
    path('student/bookings/edit/<int:pk>',views.edit_student_resource_booking,name='edit_student_resource_booking'),
    
    path('report/resource/bookings',views.ResourceBookingsReportList.as_view(),name='resource_bookings_report'),
    path('report/resource/bookings/filter',views.resource_bookings_report_filter,name='resource_bookings_report_filter'),
    path('report/resource/booking/<str:filterstr>/export/xls',print_resource_list_excel,name='print_resource_list_excel'),
    path('report/resource/booking/<str:filterstr>/export/pdf',views.create_resources_report_pdf,name='create_resources_report_pdf'),
]