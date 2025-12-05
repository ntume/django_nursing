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
from resource_management.print_resource_report_pdf import MyPrintResourceReport
from students.models import Student, StudentLearningProgrammeRegistration, StudentRegistrationLeave
from college.models import Staff

from .models import *
from .forms import *

# Create your views here.
class ResourceList(LoginRequiredMixin,ListView):
    template_name = 'resource_management/resources.html'
    context_object_name = 'items'
    model = Resource

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resources_menu'] = '--active'
        context['resources_menu_open'] = 'side-menu__sub-open'
        context['staffs'] = Staff.objects.all()
        return context


@login_required()
def add_resource(request):

    form = ResourceForm(request.POST)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.user = request.user
        resource.save()
        messages.success(request,'Successfully saved resource')
    else:
        messages.warning(request,form.errors)

    return redirect('resources:resources')

@login_required()
def edit_resource(request,pk):

    resource_instance = Resource.objects.get(id=pk)
    form = ResourceForm(request.POST,instance=resource_instance)

    if form.is_valid():
        form.save()
        messages.success(request,'Successfully edited resource')
    else:
        messages.warning(request,form.errors)

    return redirect('resources:resources')

@login_required()
def delete_resource(request,pk):

    try:
        resource_instance = Resource.objects.get(id=pk)
        resource_instance.delete()
        messages.success(request, 'Successfully deleted resource')
    except Exception as e:
        messages.warning(request, str(e))

    return redirect('resources:resources')


@login_required()
def add_resource_administrators(request,pk):

    resource = Resource.objects.get(id = pk)
    admins = request.POST.getlist('staff[]')
    
    for admin in admins:
        user = User.objects.get(id = admin)
        resource.admins.add(user)

    messages.success(request,'Successfully added resource administrators')
    
    return redirect('resources:resources')


@login_required()
def remove_resource_administrator(request,pk,admin_pk):

    resource = Resource.objects.get(id = pk)
    admin = User.objects.get(id = admin_pk)
    
    resource.admins.remove(admin)

    messages.success(request,'Successfully removed admin from resource')
    
    return redirect('resources:resources')


@login_required()
def resource_booking_student_list(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user_id = request.user.id)

        resource_bookings = ResourceBooking.objects.filter(user = request.user)      
        today = date.today()
        date_display = today.strftime("%Y-%m-%d")
        resources = Resource.objects.all()
        
        timetable = None


        all_leave = StudentRegistrationLeave.objects.filter(registration__student_learning_programme__student = student)
        
        registration_check = StudentLearningProgrammeRegistration.objects.filter(student_learning_programme__student = student,
                                                                           registration_period__start_date__lte = today,
                                                                           registration_period__end_date__gte = today)
        
        if registration_check.exists():
            registration = registration_check.last()
            timetable = registration.education_plans.all()
        
        return render(request,'resource_management/resource_booking_student.html',{
                                                                        'resources':resources,
                                                                        'resource_bookings':resource_bookings,                                                                   
                                                                        'today':today,
                                                                        'all_leave':all_leave,
                                                                        'resources_menu':'--active',
                                                                        'timetable':timetable})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def student_request_resource_booking(request):
    
    if request.user.logged_in_role_id == 10:

        form = ResourceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role      
            booking.resource_id = request.POST['resource']
            booking.save()   
            messages.success(request, "Successfully requested resource booking")
            admins = booking.resource.admins
            for admin in admins:
                to = admin.email
                name = f'{admin.first_name} {admin.last_name}'
                title = f'Resource Booking: {booking.resource.resource}'
                email_body = f'There is a booking from {booking.user.first_name} {booking.user.last_name}, Role: {{booking.role.role}}. Please log onto SIMS to approve'
                send_email_general(to,name,title,email_body)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f"{field}: {error}")


        return redirect('resources:resource_booking_student_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_student_resource_booking(request,pk):
    
    if request.user.logged_in_role_id == 10:

        booking = ResourceBooking.objects.get(id = pk)
        form = ResourceBookingForm(request.POST,instance=booking)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role
            booking.number_of_slots = 1
            booking.resource_id = request.POST['resource']            
            booking.save()
            messages.success(request,"Successfully edited resource booking")
        else:
            messages.warning(request,form.errors)

        return redirect('resources:resource_booking_student_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')




class ResourceAdminBookingsList(LoginRequiredMixin,ListView):
    template_name = 'resource_management/admin_resource_bookings.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role.internal == 'No':
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ResourceAdminBookingsList, self).get(*args, **kwargs)

    def get_queryset(self):
        admin_user = self.request.user  # or User.objects.get(id=some_id)

        # Step 1: Get resources the admin manages
        admin_resources = Resource.objects.filter(admins=admin_user)

        # Step 2: Get all bookings through related Resource
        bookings = ResourceBooking.objects.filter(
            resource__resource__in=admin_resources
        ).select_related('resource', 'user', 'role')
        
        return  bookings.order_by('booking_date', 'booking_time_start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_bookings_menu'] = '--active'
        context['resource_book_menu_open'] = '--active',
        context['resource_admin_menu_open'] = '--active',
        context['resource_bookings_menu_open'] = 'side-menu__sub-open',
        context['roles'] = Role.objects.all()
        context['admin_resources'] = Resource.objects.filter(admins=self.request.user)
        return context
    
@login_required()
def resource_bookings_filter(request):

    if request.user.logged_in_role.internal == 'Yes':
        # Step 1: Get facilities the admin manages
        admin_resources = Resource.objects.filter(admins=request.user )

        # Step 2: Get all bookings through related FacilityActivity
        booking_list = ResourceBooking.objects.filter(
            resource__resource__in=admin_resources
        ).select_related('resource', 'user', 'role')

        if request.method == "POST":
            page = 1            
            
            if request.POST['resource'] != "0":
                booking_list = booking_list.filter(resource_id = request.POST['resource'])
            if request.POST['status'] != "0":
                booking_list = booking_list.filter(status = request.POST['status'])
            if request.POST['role'] != "0":
                booking_list = booking_list.filter(role_id = request.POST['role'])
            
            filter = [request.POST['resource'],request.POST['status'],request.POST['role']]
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
                    booking_list = booking_list.filter(resource_id = filter[0])
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

        resource_bookings_menu = '--active'
        resource_book_menu_open = '--active',
        resource_admin_menu_open = '--active',
        resource_bookings_menu_open = 'side-menu__sub-open',
        roles = Role.objects.all()
        admin_resources = Resource.objects.filter(admins=request.user)
        
        return render(request,'resource_management/admin_resource_bookings.html',{'resource_bookings_menu':resource_bookings_menu,
                                                                                  'filter':filterstr,
                                                                                  'resource_book_menu_open':resource_book_menu_open,
                                                                                  'resource_admin_menu_open':resource_admin_menu_open,
                                                                                  'admin_resources':admin_resources,
                                                                                  'roles':roles,
                                                                                  'resource_bookings_menu_open':resource_bookings_menu_open })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    




@login_required()
def approve_student_resource_booking(request,pk):
    
    if request.user.logged_in_role.internal == 'Yes':
        
        booking = ResourceBooking.objects.get(id = pk)
        booking.status = request.POST['status']
        booking.status_reason = request.POST['status_reason']
        booking._skip_capacity_validation = True
        booking.save()
        messages.success(request,'Booking updated successfully')

        to = booking.user.email
        name = f'{booking.user.first_name} {booking.user.last_name}'
        title = f'Resource Booking: {booking.resource.resource}'
        email_body = f'Your booking has been {booking.status} due to the following reason: {booking.status_reason}. Please log onto SIMS to review'
        send_email_general(to,name,title,email_body)

        return redirect('resources:resource_bookings')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def resource_booking_staff_list(request):
    
    if request.user.logged_in_role.internal == 'Yes':

        
        resource_bookings = ResourceBooking.objects.filter(user = request.user)      
        today = date.today()
        date_display = today.strftime("%Y-%m-%d")
        resources = Resource.objects.all()
        my_appointments = Appointment.objects.filter(assigned = request.user)
        
        
        return render(request,'resource_management/resource_booking_staff.html',{
                                                                        'resources':resources,
                                                                        'resource_bookings':resource_bookings,                                                                   
                                                                        'today':today,
                                                                        'resource_book_menu_open':'--active',
                                                                        'resource_bookings_menu':'--active',
                                                                        'resource_bookings_menu_open':'side-menu__sub-open',
                                                                        'appointments':my_appointments})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def staff_request_resource_booking(request):
    
    if request.user.logged_in_role.internal == 'Yes':

        form = ResourceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role
            booking.number_of_resources = request.POST['number_of_resources']
            booking.resource_id = request.POST['resource']     
            booking.save()
            messages.success(request, "Successfully requested resource booking")  

            admins = booking.resource.admins
            for admin in admins:
                to = admin.email
                name = f'{admin.first_name} {admin.last_name}'
                title = f'Resource Booking: {booking.resource.resource}'
                email_body = f'There is a booking from {booking.user.first_name} {booking.user.last_name}, Role: {{booking.role.role}}. Please log onto SIMS to approve'
                send_email_general(to,name,title,email_body)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f"{field}: {error}")


        return redirect('resources:resource_booking_staff_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_staff_resource_booking(request,pk):
    
    if request.user.logged_in_role.internal == 'Yes':

        booking = ResourceBooking.objects.get(id = pk)
        form = ResourceBookingForm(request.POST,instance=booking)
        if form.is_valid():
            booking = form.save(commit = False)
            booking.user = request.user
            booking.role = request.user.logged_in_role
            booking.number_of_slots = request.POST['number_of_slots']
            booking.resource_id = request.POST['resource']            
            booking.save()
            messages.success(request,"Successfully edited resource booking")
        else:
            messages.warning(request,form.errors)

        return redirect('resources:resource_booking_staff_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



class ResourceBookingsReportList(LoginRequiredMixin,ListView):
    template_name = 'resource_management/report_resource_bookings.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role.internal == 'No':
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(ResourceBookingsReportList, self).get(*args, **kwargs)

    def get_queryset(self):
        
        bookings = ResourceBooking.objects.all().select_related('resource', 'user', 'role')
        
        return  bookings.order_by('booking_date', 'booking_time_start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_resource_bookings_menu'] = '--active'
        context['report_resource_book_menu_open'] = '--active',
        context['report_resource_admin_menu_open'] = '--active',
        context['report_resource_bookings_menu_open'] = 'side-menu__sub-open',
        context['roles'] = Role.objects.all()
        context['resources'] = Resource.objects.all()
        context['filter'] = None
        return context
    
@login_required()
def resource_bookings_report_filter(request):

    if request.user.logged_in_role.internal == 'Yes':
        
        booking_list = ResourceBooking.objects.all().select_related('resource', 'user', 'role')

        if request.method == "POST":
            page = 1            
            
            if request.POST['resource'] != "0":
                booking_list = booking_list.filter(resource_id = request.POST['resource'])
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
            
            filter = [request.POST['resource'],request.POST['status'],request.POST['role'],request.POST['student_number']]
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
                    booking_list = booking_list.filter(resource_id = filter[0])
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

        report_resource_bookings_menu = '--active'
        report_resource_book_menu_open = '--active',
        report_resource_admin_menu_open = '--active',
        report_resource_bookings_menu_open = 'side-menu__sub-open',
        roles = Role.objects.all()
        resources = Resource.objects.all()
        
        return render(request,'resource_management/report_resource_bookings.html',{'report_resource_bookings_menu':report_resource_bookings_menu,
                                                                                  'filter':filterstr,
                                                                                  'report_resource_book_menu_open':report_resource_book_menu_open,
                                                                                  'report_resource_admin_menu_open':report_resource_admin_menu_open,
                                                                                  'resources':resources,
                                                                                  'roles':roles,
                                                                                  'items':items,
                                                                                  'report_resource_bookings_menu_open':report_resource_bookings_menu_open })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def create_resources_report_pdf(request,filterstr):
    '''
    Create PDF
    '''

    report_print = MyPrintResourceReport('resources.pdf', 'A4')
    filename = report_print.print_report(filterstr)

    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    raise Http404  