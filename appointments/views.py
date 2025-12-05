import os
from django.shortcuts import render, redirect,HttpResponse,Http404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date
import datetime

from appointments.print_appointment_report_pdf import MyPrintAppointmentReport
from college.models import Staff
from django_nursing import settings
from django_nursing.email_functions import send_email_appointment_alert, send_email_appointment_update

# Create your views here.
from .models import Appointment, AppointmentCategory,AppointmentRecommendation,AppointmentOutcome,AppointmentUpdate,AppointmentContact,AppointmentNotes
from .forms import AppointmentFileForm, AppointmentForm, AppointmentCategoryForm,AppointmentRecommendationForm,AppointmentContactForm
from students.models import Student, StudentLearningProgrammeRegistration, StudentRegistrationLeave
from events.models import Event, EventType, EventRSVP
from accounts.models import User

class AppointmentCategoryListView(LoginRequiredMixin,ListView):
    template_name = 'appointments/appointment_category_list.html'
    model = AppointmentCategory
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AppointmentCategoryForm()
        context['form'] = form
        context['config_menu'] = '--active'
        context['config_menu_open'] = 'side-menu__sub-open'
        context['appt_category_menu_open'] = '--active'
        return context

@login_required()
def add_appointment_category(request):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        form = AppointmentCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Appointment category added successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('appointments:config_appointment_categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_appointment_category(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
       
        category_instance = AppointmentCategory.objects.get(id = pk)

        form = AppointmentCategoryForm(request.POST,instance = category_instance)
        if form.is_valid():
            form.save()
            messages.success(request,'Category edited successfully')
        else:
            messages.warning(request,form.errors)

          
        return redirect('appointments:config_appointment_categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def delete_appointment_category(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        category_instance = AppointmentCategory.objects.get(id = pk)
        try:
            category_instance.delete()
            messages.success(request,'Category deleted successfully')
        except Exception as e:
            messages.warning(request,str(e))

        return redirect('appointments:config_appointment_categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


class AppointmentContactListView(LoginRequiredMixin,ListView):
    template_name = 'appointments/appointment_contact_method.html'
    model = AppointmentContact
    context_object_name = 'contact_methods'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AppointmentContactForm()
        context['form'] = form
        context['config_menu'] = '--active'
        context['config_menu_open'] = 'side-menu__sub-open'
        context['appt_contact_menu_open'] = '--active'
        return context

@login_required()
def add_appointment_contact_method(request):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        form = AppointmentContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Appointment contact method added successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('appointments:config_appointment_contact_methods')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_appointment_contact_method(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
 
        contact_instance = AppointmentContact.objects.get(id = pk)
  
        form = AppointmentContactForm(request.POST,instance = contact_instance)
        if form.is_valid():
            form.save()
            messages.success(request,'Contact Method edited successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('appointments:config_appointment_contact_methods')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def delete_appointment_contact_method(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        contact_instance = AppointmentContact.objects.get(id = pk)
        try: 
            contact_instance.delete()
            messages.success(request,'Contact Method deleted successfully')
        except Exception as e:
            messages.warning(request,str(e))

        return redirect('appointments:config_appointment_contact_methods')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



class AppointmentRecommendationListView(LoginRequiredMixin,ListView):
    template_name = 'appointments/appointment_recommendations_list.html'
    model = AppointmentRecommendation
    context_object_name = 'recommendations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AppointmentRecommendationForm()
        context['form'] = form
        context['config_menu'] = '--active'
        context['config_menu_open'] = 'side-menu__sub-open'
        context['appt_recommendation_menu_open'] = '--active'
        return context

@login_required()
def add_appointment_recommendation(request):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        form = AppointmentRecommendationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Appointment recommendation added successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('appointments:config_appointment_recommendations')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def edit_appointment_recommendation(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
       
        recommendation_instance = AppointmentRecommendation.objects.get(id = pk)
 
        form = AppointmentRecommendationForm(request.POST,instance = recommendation_instance)
        if form.is_valid():
            form.save()
            messages.success(request,'Recommendation edited successfully')
        else:
            messages.warning(request,form.errors)

        return redirect('appointments:config_appointment_recommendations')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def delete_appointment_recommendation(request,pk):
    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 2:
        recommendation_instance = AppointmentRecommendation.objects.get(id = pk)
        try:
            recommendation_instance.delete()
            messages.success(request,'Recommendation deleted successfully')

        except Exception as e:
            messages.warning(request,str(e))

        return redirect('appointments:config_appointment_recommendations')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def siteconfig_appointments(request):
    try:
        site_appointments = SiteConfig.objects.get(config = 'appointments')
        if site_appointments.value == "True":
             site_appointments.value = "False"
        else:
             site_appointments.value = "True"

        site_appointments.save()
        print(site_appointments.value)
        messages.success(request, 'Appointments edited successfully')

    except Exception as e:
        messages.warning(request,str(e))

    return redirect('psycad:appointment_list')


class AllAppointmentsList(LoginRequiredMixin,ListView):
    template_name = 'appointments/appointments_all_list.html'
    context_object_name = 'all_appointments'
    paginate_by = 5

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(AllAppointmentsList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Appointment.objects.all().order_by('-appointment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appt_all_menu'] = '--active'
        context['categories'] = AppointmentCategory.objects.all()
        return context
    

@login_required()
def appointments_all_list_filter(request):
    if request.user.logged_in_role_id == 1:

        all_appointments_list = Appointment.objects.all()
        if request.method == "POST":
            page = 1
            
            if request.POST['category'] != "0":
                all_appointments_list = all_appointments_list.filter(category_id = request.POST['category'])
            if request.POST['status'] != "0":
                all_appointments_list = all_appointments_list.filter(status = request.POST['status'])
            
            filter = [request.POST['category'],request.POST['status'],]
            filterstr = '*'.join(filter)

            paginator = Paginator(all_appointments_list, 20)

            try:
                all_appointments = paginator.page(page)
            except PageNotAnInteger:
                all_appointments = paginator.page(1)
            except EmptyPage:
                all_appointments = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('*')

                if filter[0] != "":
                    all_appointments_list = all_appointments_list.filter(category_id = filter[0])
                if filter[1] != "":
                    all_appointments_list = all_appointments_list.filter(status = filter[1])
            
            paginator = Paginator(all_appointments_list, 20)
            try:
                all_appointments = paginator.page(page)
            except PageNotAnInteger:
                all_appointments = paginator.page(1)
            except EmptyPage:
                all_appointments = paginator.page(paginator.num_pages)
                
        today = date.today()
        recommendations = AppointmentRecommendation.objects.all()
        categories = AppointmentCategory.objects.all()

        return render(request,
                      'appointments/appointments_all_list.html',
                      {'all_appointments':all_appointments,
                       'filter':filterstr,
                       'today':today,
                       'recommendations':recommendations,
                       'categories':categories,
                       'appt_menu':'--active', })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
 

@login_required()
def appointments_my_list(request):
    
    if request.user.logged_in_role.internal == 'Yes':
        my_appointments = Appointment.objects.filter(assigned = request.user)
      
        today = date.today()
        recommendations = AppointmentRecommendation.objects.all()
        categories = AppointmentCategory.objects.all()
        
        return render(request,"appointments/appointments_my_list.html",{'my_appointments':my_appointments,
                                                                        'today':today,
                                                                        'recommendations':recommendations,
                                                                        'appt_menu':'--active',
                                                                        'categories':categories})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        

@login_required()
def appointments_my_list_filter(request):
    if request.user.logged_in_role.internal == 'Yes':

        my_appointments_list = Appointment.objects.filter(assigned = request.user)
        if request.method == "POST":
            page = 1
            
            if request.POST['category'] != "0":
                my_appointments_list = my_appointments_list.filter(category_id = request.POST['category'])
            if request.POST['status'] != "0":
                my_appointments_list = my_appointments_list.filter(status = request.POST['status'])
            
            filter = [request.POST['category'],request.POST['status'],]
            filterstr = '*'.join(filter)

            paginator = Paginator(my_appointments_list, 10)

            try:
                my_appointments = paginator.page(page)
            except PageNotAnInteger:
                my_appointments = paginator.page(1)
            except EmptyPage:
                my_appointments = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('*')

                if filter[0] != "":
                    my_appointments_list = my_appointments_list.filter(category_id = filter[0])
                if filter[1] != "":
                    my_appointments_list = my_appointments_list.filter(status = filter[1])
            
            paginator = Paginator(my_appointments_list, 10)
            try:
                my_appointments = paginator.page(page)
            except PageNotAnInteger:
                my_appointments = paginator.page(1)
            except EmptyPage:
                my_appointments = paginator.page(paginator.num_pages)
                
        today = date.today()
        recommendations = AppointmentRecommendation.objects.all()
        categories = AppointmentCategory.objects.all()

        return render(request,
                      'appointments/appointments_my_list.html',
                      {'my_appointments':my_appointments,
                       'filter':filterstr,
                       'today':today,
                       'recommendations':recommendations,
                       'categories':categories,
                       'appt_menu':'--active', })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def appointment_accept(request,pk):

    if request.user.logged_in_role.internal == 'Yes':
        appointment = Appointment.objects.get(id = pk)
        appointment.assigned = request.user
        appointment.status = 'Assigned'
        appointment.save()
        messages.success(request,"Successfully assigned appointment to yourself")
        update = AppointmentUpdate(appointment_id=pk,who_updates='staff',message='Appointment assigned to staff member, we will be intouch shortly')
        update.save()
        
        return redirect('appointments:appointments_my_list')
        
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

    


@login_required()
def appointment_assign(request,pk):

    try:
        appointment = Appointment.objects.get(id = pk)
        appointment.assigned_id = request.POST['consultant']
        appointment.status = 'Assigned'
        appointment.save()
        messages.success(request,f"Successfully assigned appointment")
        update = AppointmentUpdate(appointment_id=pk,who_updates='staff',message='Appointment assigned to staff member, we will be intouch shortly')
        update.save()

        fullname = f"{appointment.student.name} {appointment.student.surname}"
        department = appointment.student.department.department
        contact = appointment.student.contact_number
        email = f"{appointment.student.email}"
        category = appointment.category.category
        description = appointment.description
        appt_date = appointment.appointment_date
        appt_time = appointment.appointment_time_start

        resp = send_email_appointment_assigned([appointment.assigned.email],fullname,department,contact,email,category,description,appt_date,appt_time)

    except Exception as e:
        messages.warning(request,str(e))

    return redirect('psycad:appointment_list')


@login_required()
def appointment_remove(request,pk):

    if request.user.logged_in_role.internal == 'Yes':
        
        appointment = Appointment.objects.get(id = pk)
        appointment.assigned = None
        appointment.status = 'Pending'
        appointment.save()
        messages.success(request,"Successfully removed appointment from your list")
        return redirect('appointments:appointments_my_list')
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

    


@login_required()
def appointment_edit_status(request,pk):

    if request.user.logged_in_role.internal == 'Yes':
        
        category = None
        
        appointment = Appointment.objects.get(id = pk)
        appointment.status = request.POST['status']
        to = [appointment.student.email,]
        bcc = [request.user.email]
        name = appointment.student.first_name
        description = appointment.description
        if appointment.category:
            category = appointment.category.category
        date = appointment.appointment_date
        time = appointment.appointment_time_start

        if request.POST['status'] == "Approved":
            appointment.appointment_acceptance_feedback = request.POST['appointment_acceptance_feedback']
            message = "Appointment has been approved successfully"
            update = AppointmentUpdate(appointment_id=pk,who_updates='staff',message=request.POST['appointment_acceptance_feedback'])
            update.save()
            msg = "Your appointment has been approved"
            resp = send_email_appointment_update(to,bcc,name,description,category,date,time,request.POST['appointment_acceptance_feedback'])
        elif request.POST['status'] == "Declined":
            appointment.appointment_acceptance_feedback = request.POST['appointment_acceptance_feedback']
            message = "Appointment has been declined successfully"
            update = AppointmentUpdate(appointment_id=pk,who_updates='staff',message=request.POST['appointment_acceptance_feedback'])
            update.save()
        elif request.POST['status'] == "NewTime":
            appointment.appointment_acceptance_feedback = request.POST['appointment_acceptance_feedback']
            appointment.appointment_date = request.POST["appointment_date"]
            appointment.appointment_time_start = request.POST["appointment_time_start"]
            message = "A new time for the appointment has been suggested"
            update = AppointmentUpdate(appointment_id=pk,who_updates='staff',message='A new time for the appointment has been suggested')
            update.save()
            msg = f'A new date and time for the appointment has been suggested:  {request.POST["appointment_date"]} at {request.POST["appointment_time_start"]}'
            resp = send_email_appointment_update(to,bcc,name,description,category,request.POST["appointment_date"],request.POST["appointment_time_start"],msg)
        elif request.POST['status'] == "Completed":
            recommendations = request.POST.getlist('recommendations[]')
            priority = 1
            r = ""
            for rec in recommendations:
                r_instance = AppointmentOutcome(appointment_id = pk,recommendation_id = rec,priority = priority,user = request.user)
                r_instance.save()
                priority = priority + 1
                r = r + f" {r_instance.recommendation.recommendation},  "

            message = "Appointment completed successfully."
            update = AppointmentUpdate(appointment_id=pk,who_updates='staff',message='Appointment completed')
            update.save()
            msg = f"Appointment completed successfully. The following was recommended:  {r}"
            resp = send_email_appointment_update(to,bcc,name,description,category,date,time,msg[:-3])

        appointment.save()

        if 'file' in request.FILES:
            form_file = AppointmentFileForm(request.POST,request.FILES,instance=appointment)
            if form_file.exists():
                form_file.save()
                messages.success(request,'Successfully uploaded file')
            else:
                messages.warning(request,form_file.errors)
        
        messages.success(request,message)
                
        return redirect('appointments:appointments_my_list')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

    

@login_required()
def appointment_add_video_call_info(request,pk):
    try:
        appointment = Appointment.objects.get(id = pk)
        if appointment.video_call:
            video_call = AppointmentCallInfo.objects.get(id = appointment.video_call_id)
            video_call.delete()
            appointment.video_call = None
            appointment.save()
            messages.success(request,"Successfully removed video call room")
        else:
            channel = f"appointment_{appointment.id}"
            video_call = AppointmentCallInfo(room = channel,appt_id = appointment.id,type_of_appointment = "Appointment",user=request.user)
            video_call.save()

            appointment.video_call = video_call
            appointment.save()

            update = AppointmentUpdate(appointment_id=pk,who_updates='staff',message='An online Appointment Room has been reserved for you on UJCareerWiz Platform')
            update.save()

            messages.success(request,"Successfully reserved a room")


    except Exception as e:
        messages.warning(request,str(e))

    return redirect('appointments:appointments_my_list')

@login_required()
def appointment_student_list(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user_id = request.user.id)

        appointments = Appointment.objects.filter(student = student)
        form = AppointmentForm()
        today = date.today()
        date_display = today.strftime("%Y-%m-%d")
        categories = AppointmentCategory.objects.all()
        contact_methods = AppointmentContact.objects.all()
        staff = Staff.objects.all()
        
        timetable = None


        all_leave = StudentRegistrationLeave.objects.filter(registration__student_learning_programme__student = student)
        
        registration_check = StudentLearningProgrammeRegistration.objects.filter(student_learning_programme__student = student,
                                                                           registration_period__start_date__lte = today,
                                                                           registration_period__end_date__gte = today)
        
        if registration_check.exists():
            registration = registration_check.last()
            timetable = registration.education_plans.all()
        
        return render(request,'appointments/appointments_student.html',{'categories':categories,
                                                                        'appointments':appointments,
                                                                        'form':form,
                                                                        'today':today,
                                                                        'all_leave':all_leave,
                                                                        'contact_methods':contact_methods,
                                                                        'appt_menu':'--active',
                                                                        'staff':staff,
                                                                        'timetable':timetable})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def request_appointment(request):
    
    if request.user.logged_in_role_id == 10:

        student = Student.objects.get(user_id = request.user.id)

        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit = False)
            appointment.student = student
            appointment.contact_id = request.POST['contact']
            appointment.category_id = request.POST['category']
            appointment.assigned_id = request.POST['assigned']
            appointment.save()
            messages.success(request,"Successfully requested appointment")
            update = AppointmentUpdate(appointment_id=appointment.id,who_updates='student',message='Appointment requested')
            update.save()

            reps_emails = []
           
            reps_emails.append(f"{appointment.assigned.email}")

            fullname = f"{student.first_name} {student.last_name}"
            department = ''
            contact = student.cellphone
            email = student.email
            category = appointment.category.category
            description = appointment.description
            appt_date = appointment.appointment_date
            appt_time = appointment.appointment_time_start

            resp = send_email_appointment_alert(reps_emails,fullname,department,contact,email,category,description,appt_date,appt_time)

        else:
            messages.warning(request,form.errors)

        return redirect('appointments:appointment_student_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_appointment(request,pk):
    
    if request.user.logged_in_role_id == 10:

        appointment_instance = Appointment.objects.get(id = pk)
        form = AppointmentForm(request.POST,instance=appointment_instance)
        if form.is_valid():
            appointment = form.save(commit = False)
            appointment.contact_id = request.POST['contact']
            appointment.category_id = request.POST['category']
            appointment.assigned_id = request.POST['assigned']
            messages.success(request,"Successfully edited appointment")

            update = AppointmentUpdate(appointment_id=appointment_instance.id,who_updates='student',message='Appointment edited')
            update.save()
        else:
            messages.warning(request,form.errors)

        return redirect('appointments:appointment_student_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def appointment_new_time_accept(request,pk):

    if request.user.logged_in_role_id == 10:
        
        appointment = Appointment.objects.get(id = pk)
        appointment.status = 'New Time Accepted'
        to = [appointment.assigned.email,]
        bcc = [request.user.email]
        name = appointment.assigned.first_name
        description = appointment.description
        if appointment.category:
            category = appointment.category.category
        date = appointment.appointment_date
        time = f'{appointment.appointment_time_start} to {appointment.appointment_time_end}'

        message = "New Time has been accepted"
        update = AppointmentUpdate(appointment_id=pk,who_updates='student',message='New Time has been accepted')
        update.save()
        msg = "Your proposed time has been accepted"
        resp = send_email_appointment_update(to,bcc,name,description,category,date,time,'New Time for the appointment has been accepted')
        
        appointment.save()
        messages.success(request,message)
                
        return redirect('appointments:appointment_student_list')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def appointment_new_time_reject(request,pk):

    if request.user.logged_in_role_id == 10:
        
        appointment = Appointment.objects.get(id = pk)
        appointment.status = 'New Time Rejected'
        to = [appointment.assigned.email,]
        bcc = [request.user.email]
        name = appointment.assigned.first_name
        description = appointment.description
        if appointment.category:
            category = appointment.category.category
        date = appointment.appointment_date
        time = f'{appointment.appointment_time_start} to {appointment.appointment_time_end}'

        message = "New Time has been Rejected"
        update = AppointmentUpdate(appointment_id=pk,who_updates='student',message='New Time has been Rejected')
        update.save()
        msg = "Your proposed time has been Rejected"
        resp = send_email_appointment_update(to,bcc,name,description,category,date,time,'New Time for the appointment has been Rejected')
        
        appointment.save()
        messages.success(request,message)
                
        return redirect('appointments:appointment_student_list')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def appointment_feedback(request,pk):
    
    if request.user.logged_in_role_id == 10:

        appointment = Appointment.objects.get(id = pk)
        appointment.feedback_student = request.POST['feedback_student']
        appointment.save()
        messages.success(request,"Successfully added feedback")
        update = AppointmentUpdate(appointment_id=appointment.id,who_updates='student',message='Student feedback added')
        update.save()

        return redirect('appointments:appointment_student_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def calendar_view(request):
    LecturerUser = Lecturer.objects.get(user_id = request.user.id)
    lecturers = Lecturer.objects.filter(department = LecturerUser.department)
    visit_list = StudentSubjectVisits.objects.filter(studentsubject__subject__program__department = LecturerUser.department)
    event_list = LecturerUser.department.faculty.events.all().order_by('event_date')
    today = date.today()
    date_display = today.strftime("%Y-%m-%d")

    return render(request,'appointments/calendar.html',{'calendar_menu':'active','visit_list':visit_list,'today':date_display,'event_list':event_list})


@login_required()
def appointment_add_notes(request,pk):

    if request.user.logged_in_role.internal == 'Yes':
        add_note = AppointmentNotes(appointment_id = pk,notes = request.POST["note"],user = request.user)
        add_note.save()
        messages.success(request,"Successfully added note")
        return redirect('appointments:appointments_my_list')
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

    


@login_required()
def appointment_delete_notes(request,pk):

    if request.user.logged_in_role.internal == 'Yes':
        note = AppointmentNotes.objects.get(id = pk)
        note.delete()
        messages.success(request,"Successfully deleted note")
        return redirect('appointments:appointments_my_list')
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

    


@login_required()
def ajax_add_appointment_note(request):
    appt_id = request.GET.get('appointment_id', None)
    note = request.GET.get('note', None)
    try:
        add_note = AppointmentNotes(appointment_id = appt_id,notes = note,user = request.user)
        add_note.save()
        data = { 'is_successful': True,'id':add_note.id }
    except:
        data = { 'is_successful': False }

    return JsonResponse(data)


@login_required()
def ajax_delete_appointment_note(request):
    note_id = request.GET.get('note_id', None)
    try:
        note = AppointmentNotes.objects.get(id = note_id)
        note.delete()
        data = { 'is_successful': True }
    except:
        data = { 'is_successful': False }

    return JsonResponse(data)


@login_required()
def ajax_remove_token(request,video_id):
    #video_id = request.Get['video_call_info_id']
    try:
        video = AppointmentCallInfo.objects.get(id=video_id)
        video.token = None
        video.completed = 'Yes'
        video.save()
        data = { 'is_successful': True }
    except:
        data = { 'is_successful': False }

    return JsonResponse(data)


@login_required()
def appointments_report_list(request):
    
    if request.user.logged_in_role.internal == 'Yes':
        report_appointments = Appointment.objects.all()
      
        today = date.today()
        recommendations = AppointmentRecommendation.objects.all()
        categories = AppointmentCategory.objects.all()
        
        return render(request,"appointments/appointments_report_list.html",{'report_appointments':report_appointments,
                                                                        'today':today,
                                                                        'recommendations':recommendations,
                                                                        'report_appt_menu':'--active',
                                                                        'categories':categories,
                                                                        'filter':None})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
        

@login_required()
def appointments_report_list_filter(request):
    if request.user.logged_in_role.internal == 'Yes':

        report_appointments_list = Appointment.objects.all()
        if request.method == "POST":
            page = 1
            
            if request.POST['category'] != "0":
                report_appointments_list = report_appointments_list.filter(category_id = request.POST['category'])
            if request.POST['status'] != "0":
                report_appointments_list = report_appointments_list.filter(status = request.POST['status'])
            if request.POST['student_number'] != "":
                report_appointments_list = report_appointments_list.filter(student__student_number = request.POST['student_number'])
            if request.POST['assigned'] != "0":
                report_appointments_list = report_appointments_list.filter(assigned_id = request.POST['assigned'])
            # Outcome
            if request.POST['outcome'] != "0":
                report_appointments_list = report_appointments_list.filter(outcome__recommendation_id=request.POST['outcome'])

    
            filter = [request.POST['category'],
                      request.POST['status'],
                      request.POST['student_number'],
                      request.POST['assigned'],
                      request.POST['outcome']]
            filterstr = '*'.join(filter)

            paginator = Paginator(report_appointments_list, 10)

            try:
                report_appointments = paginator.page(page)
            except PageNotAnInteger:
                report_appointments = paginator.page(1)
            except EmptyPage:
                report_appointments = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('*')

                if filter[0] != "":
                    my_appointments_list = my_appointments_list.filter(category_id = filter[0])
                if filter[1] != "":
                    my_appointments_list = my_appointments_list.filter(status = filter[1])
                if filter[2] != "":
                    report_appointments_list = report_appointments_list.filter(student__student_number = filter[2])
                if filter[3] != "0":
                    report_appointments_list = report_appointments_list.filter(assigned_id = filter[3])
                # Outcome
                if filter[4] != "0":
                    report_appointments_list = report_appointments_list.filter(outcome__recommendation_id=filter[4])

            
            paginator = Paginator(report_appointments_list, 10)
            try:
                report_appointments = paginator.page(page)
            except PageNotAnInteger:
                report_appointments = paginator.page(1)
            except EmptyPage:
                report_appointments = paginator.page(paginator.num_pages)
                
        today = date.today()
        recommendations = AppointmentRecommendation.objects.all()
        categories = AppointmentCategory.objects.all()

        return render(request,
                      'appointments/appointments_report_list.html',
                      {'report_appointments':report_appointments,
                       'filter':filterstr,
                       'today':today,
                       'recommendations':recommendations,
                       'categories':categories,
                       'appt_menu':'--active', })

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def create_appointment_report_pdf(request,filterstr):
    '''
    Create PDF
    '''

    report_print = MyPrintAppointmentReport('resources.pdf', 'A4')
    filename = report_print.print_report(filterstr)

    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    raise Http404  