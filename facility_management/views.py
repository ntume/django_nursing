import csv
from datetime import date
from io import StringIO
import os
from django.shortcuts import render, redirect,HttpResponse,Http404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.http import JsonResponse
from collections import defaultdict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from appointments.models import Appointment
from django_nursing import settings
from django_nursing.email_functions import send_email_general
from facility_management.print_facility_list_pdf import MyPrintFacilityReport
from students.models import Student, StudentLearningProgrammeRegistration, StudentRegistrationLeave
from college.models import Staff

from .models import *
from .forms import *

# Create your views here.
class ActivityList(LoginRequiredMixin,ListView):
    template_name = 'facility_management/activities.html'
    context_object_name = 'activities'
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facilities_menu'] = '--active'
        context['facilities_menu_open'] = 'side-menu__sub-open'
        context['activity_menu_open'] = '--active'
        return context


@login_required()
def add_activity(request):

    form = ActivityForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request,'Successfully saved activity')
    else:
        messages.warning(request,form.errors)

    return redirect('facilities:activities')

@login_required()
def edit_activity(request,pk):

    activity_instance = Activity.objects.get(id=pk)
    form = ActivityForm(request.POST,instance=activity_instance)

    if form.is_valid():
        form.save()
        messages.success(request,'Successfully edited activity')
    else:
        messages.warning(request,form.errors)

    return redirect('facilities:activities')

@login_required()
def delete_activity(request,pk):

    try:
        activity_instance = Activity.objects.get(id=pk)
        activity_instance.delete()
        messages.success(request, 'Successfully deleted activity')
    except Exception as e:
        messages.warning(request, str(e))

    return redirect('facilities:activities')


class FacilityList(LoginRequiredMixin,ListView):
    template_name = 'facility_management/facilities.html'
    context_object_name = 'items'
    model = Facility

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facilities_menu'] = '--active'
        context['facilities_menu_open'] = 'side-menu__sub-open'
        context['facility_menu_open'] = '--active'
        context['activities'] = Activity.objects.all()
        context['staffs'] = Staff.objects.all()
        return context


@login_required()
def add_facility(request):

    form = FacilityForm(request.POST)
    if form.is_valid():
        facility = form.save(commit=False)
        facility.user = request.user
        facility.save()
        messages.success(request,'Successfully saved facility')
    else:
        messages.warning(request,form.errors)

    return redirect('facilities:facilities')

@login_required()
def edit_facility(request,pk):

    facility_instance = Facility.objects.get(id=pk)
    form = FacilityForm(request.POST,instance=facility_instance)

    if form.is_valid():
        form.save()
        messages.success(request,'Successfully edited facility')
    else:
        messages.warning(request,form.errors)

    return redirect('facilities:facilities')

@login_required()
def delete_facility(request,pk):

    try:
        facility_instance = Facility.objects.get(id=pk)
        facility_instance.delete()
        messages.success(request, 'Successfully deleted facility')
    except Exception as e:
        messages.warning(request, str(e))

    return redirect('facilities:facilities')


@login_required()
def add_facility_activity(request,pk):

    facility = Facility.objects.get(id = pk)
    activity = Activity.objects.get(id = request.POST['activity'])
    
    FacilityActivity.objects.create(
        facility=facility,
        activity=activity,
        capacity=request.POST['capacity']
    )

    messages.success(request,'Successfully added facility activity')
    
    return redirect('facilities:facilities')


@login_required()
def edit_facility_activity(request,pk,activity_pk):

    facility = Facility.objects.get(id = pk)
    activity = Activity.objects.get(id = activity_pk)
    
    facility_activities = FacilityActivity.objects.filter(
        facility=facility,
        activity=activity,
        capacity=request.POST['capacity']
    )
    
    if facility_activities.exists():
        facility_activity = facility_activities.first()
        facility_activity.capacity = request.POST['capacity']
        facility_activity.save()
        
        messages.success(request,'Successfully updated capacity')

    messages.success(request,'Successfully added facility activity')
    
    return redirect('facilities:facilities')


@login_required()
def remove_facility_activity(request,pk,activity_pk):

    facility = Facility.objects.get(id = pk)
    activity = Activity.objects.get(id = activity_pk)
    
    FacilityActivity.objects.filter(
        facility=facility,
        activity=activity,
        capacity=request.POST['capacity']
    ).delete()

    messages.success(request,'Successfully removed activity from facility')
    
    return redirect('facilities:facilities')



@login_required()
def add_facility_administrators(request,pk):

    facility = Facility.objects.get(id = pk)
    admins = request.POST.getlist('staff[]')
    
    for admin in admins:
        user = User.objects.get(id = admin)
        facility.admins.add(user)

    messages.success(request,'Successfully added facility administrators')
    
    return redirect('facilities:facilities')


@login_required()
def remove_facility_administrator(request,pk,admin_pk):

    facility = Facility.objects.get(id = pk)
    admin = User.objects.get(id = admin_pk)
    
    facility.admins.remove(admin)

    messages.success(request,'Successfully removed admin from facility')
    
    return redirect('facilities:facilities')


@login_required()
def facility_booking_student_list(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user_id = request.user.id)

        facility_bookings = FacilityActivityBooking.objects.filter(user = request.user)      
        today = date.today()
        date_display = today.strftime("%Y-%m-%d")
        facilities = Facility.objects.all()
        
        timetable = None


        all_leave = StudentRegistrationLeave.objects.filter(registration__student_learning_programme__student = student)
        
        registration_check = StudentLearningProgrammeRegistration.objects.filter(student_learning_programme__student = student,
                                                                           registration_period__start_date__lte = today,
                                                                           registration_period__end_date__gte = today)
        
        if registration_check.exists():
            registration = registration_check.last()
            timetable = registration.education_plans.all()
        
        return render(request,'facility_management/facility_booking_student.html',{
                                                                        'facilities':facilities,
                                                                        'facility_bookings':facility_bookings,                                                                   
                                                                        'today':today,
                                                                        'all_leave':all_leave,
                                                                        'facilities_menu':'--active',
                                                                        'timetable':timetable})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def student_request_facility_booking(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user_id = request.user.id)

        form = FacilityActivityBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role
            booking.number_of_slots = 1
            booking.facility_activity_id = request.POST['facility_activity']        
            booking.save()
            messages.success(request, "Successfully requested facility booking")    
            admins = booking.facility_activity.facility.admins
            for admin in admins:
                to = admin.email
                name = f'{admin.first_name} {admin.last_name}'
                title = f'Facility Booking: {booking.facility_activity.facility.facility}'
                email_body = f'There is a booking from {booking.user.first_name} {booking.user.last_name}, Role: { booking.role.role }. Please log onto SIMS to approve'
                send_email_general(to,name,title,email_body)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f"{field}: {error}")


        return redirect('facilities:facility_booking_student_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_student_facility_booking(request,pk):
    
    if request.user.logged_in_role_id == 10:

        booking = FacilityActivityBooking.objects.get(id = pk)
        form = FacilityActivityBookingForm(request.POST,instance=booking)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role
            booking.number_of_slots = 1
            booking.facility_activity_id = request.POST['facility_activity']            
            booking.save()
            messages.success(request,"Successfully edited facility booking")
        else:
            messages.warning(request,form.errors)

        return redirect('facilities:facility_booking_student_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


class FacilityAdminBookingsList(LoginRequiredMixin,ListView):
    template_name = 'facility_management/admin_facility_bookings.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role.internal == 'No':
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(FacilityAdminBookingsList, self).get(*args, **kwargs)

    def get_queryset(self):
        admin_user = self.request.user  # or User.objects.get(id=some_id)

        # Step 1: Get facilities the admin manages
        admin_facilities = Facility.objects.filter(admins=admin_user)

        # Step 2: Get all bookings through related FacilityActivity
        bookings = FacilityActivityBooking.objects.filter(
            facility_activity__facility__in=admin_facilities
        ).select_related('facility_activity', 'user', 'role')
        
        return  bookings.order_by('booking_date', 'booking_time_start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facility_bookings_menu'] = '--active'
        context['facility_book_menu_open'] = '--active',
        context['facility_admin_menu_open'] = '--active',
        context['admin_facilities'] = Facility.objects.filter(admins=self.request.user)
        context['roles'] = Role.objects.all()
        context['facility_bookings_menu_open'] = 'side-menu__sub-open',
        return context
    
@login_required()
def facility_bookings_filter(request):

    if request.user.logged_in_role.internal == 'Yes':
        # Step 1: Get facilities the admin manages
        admin_facilities = Facility.objects.filter(admins=request.user )

        # Step 2: Get all bookings through related FacilityActivity
        booking_list = FacilityActivityBooking.objects.filter(
            facility_activity__facility__in=admin_facilities
        ).select_related('facility_activity', 'user', 'role')

        if request.method == "POST":
            page = 1            
            
            if request.POST['facility'] != "0":
                booking_list = booking_list.filter(facility_activity__facility_id = request.POST['facility'])
            if request.POST['status'] != "0":
                booking_list = booking_list.filter(status = request.POST['status'])
            if request.POST['role'] != "0":
                booking_list = booking_list.filter(role_id = request.POST['role'])
            
            filter = [request.POST['facility'],request.POST['status'],request.POST['role']]
            filterstr = '-'.join(filter)

            paginator = Paginator(booking_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "0":
                    booking_list = booking_list.filter(facility_activity__facility_id = filter[0])
                if filter[1] != "0":
                    booking_list = booking_list.filter(status = filter[1])
                if filter[2] != "0":
                    booking_list = booking_list.filter(role_id = filter[2])
       
            paginator = Paginator(booking_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        facility_bookings_menu = '--active'
        facility_book_menu_open = '--active',
        facility_admin_menu_open = '--active',
        admin_facilities = Facility.objects.filter(admins=request.user)
        roles = Role.objects.all()
        facility_bookings_menu_open = 'side-menu__sub-open',
        
        return render(request,'facility_management/admin_facility_bookings.html',{'facility_bookings_menu':facility_bookings_menu,
                                                                                  'filter':filterstr,
                                                                                  'facility_book_menu_open':facility_book_menu_open,
                                                                                  'facility_admin_menu_open':facility_admin_menu_open,
                                                                                   'admin_facilities':admin_facilities,
                                                                                   'roles':roles,
                                                                                   'facility_bookings_menu_open':facility_bookings_menu_open })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def approve_student_facility_booking(request,pk):
    
    if request.user.logged_in_role.internal == 'Yes':
        
        booking = FacilityActivityBooking.objects.get(id = pk)
        booking.status = request.POST['status']
        booking.status_reason = request.POST['status_reason']
        booking._skip_capacity_validation = True
        booking.save()
        messages.success(request,'Booking updated successfully')

        to = booking.user.email
        name = f'{booking.user.first_name} {booking.user.last_name}'
        title = f'Facility Booking: {booking.facility_activity.facility.facility}'
        email_body = f'Your booking has been {booking.status} due to the following reason: {booking.status_reason}. Please log onto SIMS to review'
        send_email_general(to,name,title,email_body)

        return redirect('facilities:facility_bookings')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
    

@login_required()
def facility_booking_staff_list(request):
    
    if request.user.logged_in_role.internal == 'Yes':

        
        facility_bookings = FacilityActivityBooking.objects.filter(user = request.user)      
        today = date.today()
        date_display = today.strftime("%Y-%m-%d")
        facilities = Facility.objects.all()
        my_appointments = Appointment.objects.filter(assigned = request.user)
        
        
        return render(request,'facility_management/facility_booking_staff.html',{
                                                                        'facilities':facilities,
                                                                        'facility_bookings':facility_bookings,                                                                   
                                                                        'today':today,
                                                                        'facilities_menu':'--active',
                                                                        'facility_bookings_menu':'--active',
                                                                        'facility_bookings_menu_open':'side-menu__sub-open',
                                                                        'appointments':my_appointments})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def staff_request_facility_booking(request):
    
    if request.user.logged_in_role.internal == 'Yes':

        form = FacilityActivityBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role
            booking.number_of_slots = request.POST['number_of_slots']
            booking.facility_activity_id = request.POST['facility_activity']   
            booking.save()
            messages.success(request, "Successfully requested facility booking")
                 
            admins = booking.facility_activity.facility.admins
            for admin in admins:
                to = admin.email
                name = f'{ admin.first_name } { admin.last_name }'
                title = f'Facility Booking: { booking.facility_activity.facility.facility }'
                email_body = f'There is a booking from { booking.user.first_name } { booking.user.last_name }, Role: { booking.role.role }. Please log onto SIMS to approve'
                send_email_general(to,name,title,email_body)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f"{field}: {error}")


        return redirect('facilities:facility_booking_staff_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_staff_facility_booking(request,pk):
    
    if request.user.logged_in_role.internal == 'Yes':

        booking = FacilityActivityBooking.objects.get(id = pk)
        form = FacilityActivityBookingForm(request.POST,instance=booking)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role
            booking.number_of_slots = request.POST['number_of_slots']
            booking.facility_activity_id = request.POST['facility_activity']            
            booking.save()
            messages.success(request,"Successfully edited facility booking")
        else:
            messages.warning(request,form.errors)

        return redirect('facilities:facility_booking_staff_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


class FacilityBookingsReportList(LoginRequiredMixin,ListView):
    template_name = 'facility_management/report_facility_bookings.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role.internal == 'No':
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(FacilityBookingsReportList, self).get(*args, **kwargs)

    def get_queryset(self):
        
        bookings = FacilityActivityBooking.objects.all().select_related('facility_activity', 'user', 'role')
        
        return  bookings.order_by('booking_date', 'booking_time_start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_facility_bookings_menu'] = '--active'
        context['report_facility_book_menu_open'] = '--active',
        context['report_facility_admin_menu_open'] = '--active',
        context['facilities'] = Facility.objects.all()
        context['roles'] = Role.objects.all()
        context['report_facility_bookings_menu_open'] = 'side-menu__sub-open',
        context['filter'] = None
        return context
    
@login_required()
def facility_bookings_report_filter(request):

    if request.user.logged_in_role.internal == 'Yes':
        
        booking_list = FacilityActivityBooking.objects.all().select_related('facility_activity', 'user', 'role')

        if request.method == "POST":
            page = 1            
            
            if request.POST['facility_activity'] != "0":
                booking_list = booking_list.filter(facility_activity_id = request.POST['facility_activity'])
            if request.POST['status'] != "0":
                booking_list = booking_list.filter(status = request.POST['status'])
            if request.POST['role'] != "0":
                if request.POST['role'] == "10":
                    booking_list = booking_list.filter(role_id = request.POST['role'])
                else:
                    booking_list = booking_list.exclude(role_id = 10)
            if request.POST['student_number'] != "":
                student = Student.objects.filter(student_number = request.POST['student_number']).first()
                if student:
                    booking_list = booking_list.filter(user = student.user)
            
            filter = [request.POST['facility_activity'],request.POST['status'],request.POST['role'],request.POST['student_number']]
            filterstr = '-'.join(filter)

            paginator = Paginator(booking_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "0":
                    booking_list = booking_list.filter(facility_activity_id = filter[0])
                if filter[1] != "0":
                    booking_list = booking_list.filter(status = filter[1])
                if filter[2] != "0":
                    if filter[2]== "10":
                        booking_list = booking_list.filter(role_id = filter[2])
                    else:
                        booking_list = booking_list.exclude(role_id = 10)
                if filter[3] != "":
                    student = Student.objects.filter(student_number = filter[3]).first()
                    if student:
                        booking_list = booking_list.filter(user = student.user)
       
            paginator = Paginator(booking_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        report_facility_bookings_menu = '--active'
        report_facility_book_menu_open = '--active',
        report_facility_admin_menu_open = '--active',
        facilities = Facility.objects.all()
        roles = Role.objects.all()
        report_facility_bookings_menu_open = 'side-menu__sub-open',
        
        return render(request,'facility_management/report_facility_bookings.html',{'report_facility_bookings_menu':report_facility_bookings_menu,
                                                                                  'filter':filterstr,
                                                                                  'report_facility_book_menu_open':report_facility_book_menu_open,
                                                                                  'report_facility_admin_menu_open':report_facility_admin_menu_open,
                                                                                  'facilities':facilities,
                                                                                  'roles':roles,
                                                                                  'items':items,
                                                                                  'report_facility_bookings_menu_open':report_facility_bookings_menu_open })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def create_facilities_report_pdf(request,filterstr):
    '''
    Create PDF
    '''

    report_print = MyPrintFacilityReport('facilities.pdf', 'A4')
    filename = report_print.print_report(filterstr)

    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    raise Http404  