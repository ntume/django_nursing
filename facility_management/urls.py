from django.urls import path

from facility_management.print_facility_list_excel import print_facility_list_excel

from . import views

app_name = 'facility'

urlpatterns = [
        
    path('admin/activity/',views.ActivityList.as_view(),name='activities'),
    path('admin/activity/add',views.add_activity,name='add_activity'),
    path('admin/activity/<int:pk>/edit',views.edit_activity,name='edit_activity'),   
    path('admin/activity/<int:pk>/delete',views.delete_activity,name='delete_activity'), 
    
    path('admin/facility/',views.FacilityList.as_view(),name='facilities'),
    path('admin/facility/add',views.add_facility,name='add_facility'),
    path('admin/facility/<int:pk>/edit',views.edit_facility,name='edit_facility'),   
    path('admin/facility/<int:pk>/delete',views.delete_facility,name='delete_facility'),   
    path('admin/facility/<int:pk>/activity/add',views.add_facility_activity,name='add_facility_activity'), 
    path('admin/facility/<int:pk>/activity/<int:activity_pk>/edit',views.edit_facility_activity,name='edit_facility_activity'), 
    path('admin/facility/<int:pk>/activity/<int:activity_pk>/remove',views.remove_facility_activity,name='remove_facility_activity'),

    path('admin/facility/<int:pk>/admins/add',views.add_facility_administrators,name='add_facility_administrators'), 
    path('admin/facility/<int:pk>/admins/<int:admin_pk>/remove',views.remove_facility_administrator,name='remove_facility_administrator'),

    path('admin/facility/bookings',views.FacilityAdminBookingsList.as_view(),name='facility_bookings'),
    path('admin/facility/bookings/filter',views.facility_bookings_filter,name='facility_bookings_filter'),
    path('admin/facility/booking/<int:pk>/approve',views.approve_student_facility_booking,name='approve_student_facility_booking'),
    
    path('staff/facility/bookings',views.facility_booking_staff_list,name='facility_booking_staff_list'),
    path('staff/facility/booking/request/',views.staff_request_facility_booking,name='staff_request_facility_booking'),
    path('staff/facility/booking/<int:pk>/edit',views.edit_staff_facility_booking,name='edit_staff_facility_booking'),

    path('student/bookings/',views.facility_booking_student_list,name='facility_booking_student_list'),
    path('student/bookings/request',views.student_request_facility_booking,name='student_request_facility_booking'),
    path('student/bookings/edit/<int:pk>',views.edit_student_facility_booking,name='edit_student_facility_booking'),
    
    path('report/facility/bookings',views.FacilityBookingsReportList.as_view(),name='facility_bookings_report'),
    path('report/facility/bookings/filter',views.facility_bookings_report_filter,name='facility_bookings_report_filter'),
    path('report/facility/booking/<str:filterstr>/excel/export',print_facility_list_excel,name='print_facility_list_excel'),
    path('report/facility/booking/<str:filterstr>/pdf/export',views.create_facilities_report_pdf,name='create_facilities_report_pdf'),
    
    
]