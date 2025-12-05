from django.shortcuts import render, redirect,HttpResponse,Http404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime
import random
import datetime as dt
import pytz
import os
from io import BytesIO
import os
import datetime
import csv
import xlwt
import json
from datetime import date
import uuid
import openpyxl
from io import BytesIO

from .models import * 
from students.models import Student,EmailPreferences
from .forms import *
from .print_registration_form import MyPrint,PdfCreator
from .print_registrations import MyPrintReg,PdfCreatorReg
from django_nursing.email_functions import send_email_event_registration,send_email_event_registration_alert,send_email_student_event_message,send_email_general_message



# Create your views here.

def send_sendgrid_email_general(sender_name,sender_email,from_email,to,name,msg,subject,title):
    
    message = Mail(
    from_email=from_email,
    to_emails=to)

    message.dynamic_template_data = {
    'name': name,
    'message': msg,
    'subject':subject,
    'title':title,
    'sender_name':sender_name,
    'sender_email':sender_email
    }

    message.template_id = 'd-6c1a1245015d47ae9d568523c423abf5'

    try:
        sg = SendGridAPIClient('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')

        response = sg.send(message)

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))


class EventList(LoginRequiredMixin,ListView):
    template_name = 'events/list.html'
    context_object_name = 'events'

    def get_queryset(self):
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        events_all = StudentUser.department.faculty.events.filter(event_date_end__gte=datetime.date.today(),published__exact='Yes').order_by('event_date')
        events = []
        for event in events_all:
            if event.invitees == "1" or event.invitees =="3":
                _event = {'id':event.id,'title':event.title,'type':event.type.type,'description':event.description,'event_date':event.event_date,'event_date_end':event.event_date_end,'event_time':event.event_time,'event_time_end':event.event_time_end,'registration':event.registration,'location':event.location,'extra_information':event.extra_information,'media_files':event.media_files.all(),'file':event.file}
                print(_event['media_files'])
                chckrsvpexists = EventRSVP.objects.filter(student=StudentUser,event=event).exists()
                if chckrsvpexists:
                    _event['rsvp'] = True
                else:
                    _event['rsvp'] = False

                events.append(_event)

        return events


    def get_context_data(self, **kwargs):
        context = super(EventList, self).get_context_data(**kwargs)
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        context['events_menu'] = 'active'
        context['past_events'] = False
        context['title'] = f'Recruitment Programs targeted for: {StudentUser.department.faculty.faculty}'
        return context


class EventListAll(LoginRequiredMixin,ListView):
    template_name = 'events/list.html'
    context_object_name = 'events'

    def get_queryset(self):
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        events_all = Event.objects.filter(event_date_end__gte=datetime.date.today(),published__exact='Yes').order_by('event_date')
        events = []
        for event in events_all:
            if event.invitees == "1" or event.invitees =="3":
                _event = {'id':event.id,'title':event.title,'type':event.type.type,'description':event.description,'event_date':event.event_date,'event_date_end':event.event_date_end,'event_time':event.event_time,'event_time_end':event.event_time_end,'registration':event.registration,'location':event.location,'extra_information':event.extra_information,'media_files':event.media_files.all(),'file':event.file}
                print(_event['media_files'])
                chckrsvpexists = EventRSVP.objects.filter(student=StudentUser,event=event).exists()
                if chckrsvpexists:
                    _event['rsvp'] = True
                else:
                    _event['rsvp'] = False

                events.append(_event)

        return events


    def get_context_data(self, **kwargs):
        context = super(EventListAll, self).get_context_data(**kwargs)
        context['events_menu'] = 'active'
        context['past_events'] = False
        context['title'] = "All UJ Recruitment Programs"
        return context


class EventPastList(LoginRequiredMixin,ListView):
    template_name = 'events/list.html'
    context_object_name = 'events'

    def get_queryset(self):
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        events_all = StudentUser.department.faculty.events.filter(event_date__lte=datetime.date.today(),published__exact='Yes').order_by('event_date')
        events = []
        for event in events_all:
            if event.invitees == "1" or event.invitees =="3":
                _event = {'id':event.id,'title':event.title,'type':event.type.type,'description':event.description,'event_date':event.event_date,'event_date_end':event.event_date_end,'event_time':event.event_time,'event_time_end':event.event_time_end,'registration':event.registration,'location':event.location,'extra_information':event.extra_information,'media_files':event.media_files.all()}

                chckrsvpexists = EventRSVP.objects.filter(student=StudentUser,event=event).exists()
                if chckrsvpexists:
                    _event['rsvp'] = True
                else:
                    _event['rsvp'] = False

                events.append(_event)

        return events


    def get_context_data(self, **kwargs):
        context = super(EventPastList, self).get_context_data(**kwargs)
        context['events_menu'] = 'active'
        context['past_events'] = True
        return context

class EventLectList(LoginRequiredMixin,ListView):
    template_name = 'events/list_lecturer.html'
    context_object_name = 'events'

    def get_queryset(self):
        LecturerUser = Lecturer.objects.get(user_id = self.request.user.id)
        return  LecturerUser.department.faculty.events.all().order_by('event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculties'] = Faculty.objects.all()
        context['eve_menu'] = 'active'
        return context

class EventAllList(LoginRequiredMixin,ListView):
    template_name = 'events/list_all.html'
    context_object_name = 'events'

    def get_queryset(self):
        #send_mass_email("test","testig sedndgrid",["mmuwanguzi@gmail.com","mark@wilms.co.za","info@wilms.co.za","noreply@wilms.co.za"],["noreply@wilms.co.za"])
        #sendgrid_test_email()
        return Event.objects.all().order_by('-event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = form = EventDocumentForm()
        context['space_types'] = VirtualSpaceType.objects.all()
        context['faculties'] = Faculty.objects.all()
        context['eve_menu'] = 'active'
        context['form'] = form
        return context

class EventAdminAllList(LoginRequiredMixin,ListView):
    template_name = 'events/list_all_admin.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.all().order_by('event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = form = EventDocumentForm()
        context['faculties'] = Faculty.objects.all()
        context['eve_menu'] = 'active'
        context['form'] = form
        return context

class EventRSVPList(LoginRequiredMixin,ListView):

    template_name = 'events/rsvp.html'
    context_object_name = 'student'

    def get_queryset(self):
        return Student.objects.get(user_id = self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(EventRSVPList, self).get_context_data(**kwargs)
        context['events_menu'] = 'active'
        return context


class EventCreateView(LoginRequiredMixin,CreateView):
    template_name = 'events/create.html'
    form_class = EventCreateForm
    success_message = "%(title)s was created successfully."
    error_message = "Unfortunately something went wrong, please try again"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        if 'extra_information_company' in self.request.POST:
            self.object.extra_information_company = self.request.POST['extra_information_company']

        if 'extra_information' in self.request.POST:
            self.object.extra_information = self.request.POST['extra_information']

        if self.request.POST['company_organized'] == 'Yes':
            self.object.company_id = self.request.POST['company']
        self.object.save()

        messages.success(self.request,'Successfully added Event')

        faculties = self.request.POST.getlist('faculties[]')

        for f in faculties:
            faculty = Faculty.objects.get(id = f)
            self.object.faculties.add(faculty)

        self.object.save()

        if self.request.user.roles_id == 2:
            return redirect('wil:event_list')
        elif self.request.user.roles_id == 10 or self.request.user.roles_id == 11:
            return redirect('psycad:event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculties = Faculty.objects.all().order_by("faculty")
        context['faculties'] = faculties
        context['campuses'] = Campus.objects.all()
        context['eve_menu'] = 'active'
        context['companies'] = Company.objects.all().order_by('company_name')
        return context

class EventUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'events/edit.html'
    model = Event
    context_object_name = 'event'
    pk_url_kwarg = 'pk'
    fields = ('title','description','registration','type','event_date','event_time','location','extra_information','published','invitees','company_organized','company','event_date_end','event_time_end')

    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.user = self.request.user

        if 'extra_information_company' in self.request.POST:
            self.object.extra_information_company = self.request.POST['extra_information_company']

        if 'extra_information' in self.request.POST:
            self.object.extra_information = self.request.POST['extra_information']

        if self.request.POST['company_organized'] == 'Yes':
            self.object.company_id = self.request.POST['company']
        else:
            self.object.company_id = ""

        if self.request.POST['registration_form'] != "":
            self.object.registration_form_id = self.request.POST['registration_form']
        else:
            self.object.registration_form_id = None

        self.object.campus_id = self.request.POST['campus']
        self.object.save()

        messages.success(self.request,'Successfully edited Event')

        if self.request.user.roles_id == 2:
            return redirect('wil:event_list')
        elif self.request.user.roles_id == 10 or self.request.user.roles_id == 11:
            return redirect('psycad:event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculties = Faculty.objects.all().order_by("faculty")
        context['faculties'] = faculties
        context['campuses'] = Campus.objects.all()
        context['eve_menu'] = 'active'
        context['companies'] = Company.objects.all().order_by('company_name')
        return context

@login_required()
def view_events_as(request,view_as):
    events = Event.objects.filter(event_date__gte=datetime.date.today(),published__exact='Yes').order_by('-event_date')
    if view_as == 'company_contact':
        events = events.filter(Q(invitees="2") | Q(invitees="3"))
        return render(request,'events/as_company_contact.html',{'events':events,'view_as':view_as})
    if view_as == 'student':
        events = events.filter(Q(invitees="1") | Q(invitees="3"))
        return render(request,'events/as_student.html',{'events':events,'view_as':view_as})


@login_required()
def add_event(request):

    form = EventCreateForm(request.POST)

    if form.is_valid():

        event = form.save(commit=False)
        event.user = request.user

        if 'extra_information_company' in request.POST:
            event.extra_information_company = request.POST['extra_information_company']

        if 'extra_information' in request.POST:
            event.extra_information = request.POST['extra_information']

        if request.POST['company_organized'] == 'Yes':
            event.company_id = request.POST['company']
        if 'registration_form' in request.POST:
            if request.POST['registration_form'] != "":
                event.registration_form_id = request.POST['registration_form']

        event.campus_id = request.POST['campus']
        event.save()

        messages.success(request,'Successfully added Event')

        faculties = request.POST.getlist('faculties[]')
        student_emails = []

        for f in faculties:
            faculty = Faculty.objects.get(id = f)
            event.faculties.add(faculty)
            for d in faculty.departments.all():
                for s in d.students.all():
                    try:
                        if s.email_preferences.events == 'Yes':
                            student_emails.append(s.email)
                    except:
                        pass

            #students = faculty.departments.students.email_preferences.filter(events__exact = 'Yes')

        event.save()

    else:
        messages.warning(request,form.errors)

    if request.user.roles_id == 2:
        return redirect('wil:event_list')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_list')

@login_required()
def ajax_fetch_reg_forms(request):
    type_id = request.GET.get('type_id',None)
    reg_forms = EventRegistrationForm.objects.filter(event_type_id=type_id)

    data = []
    for r in reg_forms:
        data.append({'id':r.id,'title':r.title})

    return JsonResponse(list(data), safe=False)


@login_required()
def ajax_fetch_event_info(request):
    event_id = request.GET.get('event_id',None)
    event = Event.objects.get(id=event_id)

    data = []
    data.append({'event_date':event.event_date,'event_date_end':event.event_date_end,'event_time':event.event_time,'event_time_end':event.event_time_end})

    return JsonResponse(list(data), safe=False)


@login_required()
def event_company_list(request):

    contactUser = CompanyContacts.objects.get(user_id = request.user.id)

    events = Event.objects.filter(event_date_end__gte=datetime.date.today(),published__exact='Yes').order_by('-event_date')
    events_list = events.filter(Q(invitees="2") | Q(invitees="3"))
    events_company = []
    for e in events_list:
        chck_reg_form_exits_for_event = False
        check_reg_form = EventCompanyRSVP.objects.filter(event = e, company = contactUser.company)
        if e.registration_form:
            chck_reg_form_exits_for_event = True

        if check_reg_form.exists():
            e_map = {'id':e.id,'title':e.title,'description':e.description,'type':e.type.type,'event_date':e.event_date,'event_time':e.event_time,'location':e.location,'rsvp':'Yes','reg_form_exists':chck_reg_form_exits_for_event,'check_reg_form':check_reg_form}
        else:
            e_map = {'id':e.id,'title':e.title,'description':e.description,'type':e.type.type,'event_date':e.event_date,'event_time':e.event_time,'location':e.location,'rsvp':'No','reg_form_exists':chck_reg_form_exits_for_event}

        events_company.append(e_map)

    announcements = Announcements.objects.filter(published__exact = 'Yes')

    return render(request,'events/list_company.html',{'events':events_company,'announcements':announcements})


@login_required()
def event_registration_form_company(request,pk):
    
    try:
        contactUser = CompanyContacts.objects.get(user_id = request.user.id)
        check_reg_form = EventCompanyRSVP.objects.get(id = pk)
        questions = EventRegistrationFormQuestion.objects.filter(registration_form = check_reg_form.event.registration_form.id).order_by('question_number')

        completed = True
        
        return render(request,'events/company_registration_form.html',{'event':check_reg_form.event,'check_reg_form':check_reg_form,'completed':completed,'questions':questions})

    except Exception as e:
        messages.warning(request,f"An error has occurred, please contact the administrator. Error code: {str(e)}")
        return redirect('contact:event_list')


@login_required()
def event_registration_form_company_add(request,pk):

    '''
    View to add a new form to show up
    '''
    
    try:
        contactUser = CompanyContacts.objects.get(user_id = request.user.id)
        event = Event.objects.get(id = pk)
        questions = EventRegistrationFormQuestion.objects.filter(registration_form = event.registration_form.id).order_by('question_number')

        completed = False
        
        return render(request,'events/company_registration_form.html',{'event':event,'completed':completed,'questions':questions})

    except:
        messages.warning(request,"An error has occurred, please contact the administrator")
        return redirect('contact:event_list')

    
@login_required()
def event_registration_form_view_add(request,pk):

    contactUser = CompanyContacts.objects.get(user_id = request.user.id)

    event_instance = Event.objects.get(id = pk)

    reg_form = EventRegistrationForm(id = event_instance.registration_form_id)

    if request.method == 'POST':
        
        try:

            company_registration_form = EventCompanyRSVP.objects.create(event = event_instance, company = contactUser.company,registration_form = reg_form)
            company_registration_form.save()
            company_registration_form.contacts.add(contactUser)

            for qn in reg_form.questions.all():
                if qn.choice == 'many':
                    try:
                        a = ",".join(request.POST.getlist('{}[]'.format(qn.id)))
                        answer = EventRegistrationCompanyAnswers.objects.create(answer=a,question=qn,registration_form_company=company_registration_form)
                        answer.save()
                    except:
                        pass
                else:
                    try:
                        a = request.POST['{}'.format(qn.id)]
                        answer = EventRegistrationCompanyAnswers.objects.create(answer=a,question=qn,registration_form_company=company_registration_form)
                        answer.save()
                    except:
                        pass

            messages.success(request,f'Thank you for your registration for the UJ PsyCaD Career Services: {event_instance.title}. Please wait for our confirmation before making final arrangements.')

            from_email = event_instance.user.email
            from_name = f'{event_instance.user.first_name} {event_instance.user.last_name}'
            company = contactUser.company.company_name
            contact = f'{contactUser.name} {contactUser.surname}'
            email = contactUser.email
            telephone = contactUser.telephone
            cellphone = contactUser.cellphone

            send_email_event_registration_alert(from_name,from_email,company,contact,email,telephone,cellphone)

            send_email_event_registration(email,contact,from_name,from_email)

            return redirect('contact:event_list')

        except Exception as e:
            messages.warning(request,str(e))
            return redirect('contact:event_registration_form_company',pk=pk)

    return redirect('contact:event_registration_form_company',pk=pk)


@login_required()
def event_student_view(request,pk):
    event = Event.objects.get(id = pk)
    StudentUser = Student.objects.get(user_id = request.user.id)
    chckrsvpexists = EventRSVP.objects.filter(student=StudentUser,event=event).exists()

    return render(request,'events/event_student_view.html',{'event':event,'chckrsvpexists':chckrsvpexists})

@login_required()
def event_company_view(request,pk):

    event = Event.objects.get(id=pk)
    return render(request,'events/event_company_view.html',{'event':event})

@login_required()
def event_add_media(request,pk):
    event_instance = Event.objects.get(id = pk)
    if request.POST['type'] == "Video Link":
        form = EventMediaFile(request.POST, request.FILES)
    elif request.POST['type'] == "image":
        form = EventMediaImage(request.POST, request.FILES)
    elif request.POST['type'] == "PDF file":
        form = EventMediaFile(request.POST, request.FILES)

    if form.is_valid():
        media_file = form.save(commit=False)
        media_file.event = event_instance
        media_file.save()
        messages.success(request,"Successfully added media file")
    else:
        messages.warning(request,form.errors)

    if request.user.roles_id == 2:
        return redirect('wil:event_edit',pk=pk)
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_edit',pk=pk)


@login_required()
def event_media_delete(request,event_pk,pk):
    try:
        media_instance = EventMedia.objects.get(id = pk)
        media_instance.delete()
        messages.success(request,"Successfully deleted file")
    except:
        messages.warning(request,"An error has occured, Media not deleted, please try again or contact your administrator")

    if request.user.roles_id == 2:
        return redirect('wil:event_edit',pk=event_pk)
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_edit',pk=event_pk)


@login_required()
def add_event_file(request,pk):
    event_instance = Event.objects.get(id = pk)
    form = EventDocumentForm(request.POST, request.FILES, instance = event_instance)
    if form.is_valid():
        form.save()
        messages.success(request,'Successfully uploaded file')
    else:
        messages.warning(request,form.errors)

    if request.user.roles_id == 2:
        return redirect('wil:event_list')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_list')

@login_required()
def view_rsvps(request,pk):
    event_instance = Event.objects.get(id = pk)
    rsvps = EventRSVP.objects.filter(event = event_instance)

    return render(request,'events/list_rsvps.html',{'event':event_instance,'rsvps':rsvps})

@login_required()
def view_company_rsvps(request,pk):
    event_instance = Event.objects.get(id = pk)
    rsvps = EventCompanyRSVP.objects.filter(event = event_instance)

    return render(request,'events/list_company_rsvps.html',{'event':event_instance,'rsvps':rsvps})


@login_required()
def print_rsvps_excel(request,pk):

    event_instance = Event.objects.get(id = pk)
    rsvps = event_instance.rsvp_students.all()

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="rsvps.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('rsvps')

    row_num = 0

    font_style = xlwt.XFStyle()

    font_style.font.bold = True

    rsvp = []

    rsvp.append('Student Name')
    rsvp.append('Student Number')
    rsvp.append('Contact Number')
    rsvp.append('Email')
    rsvp.append('Gender')
    rsvp.append('Race')
    rsvp.append('Nationality')
    rsvp.append('Employed')
    rsvp.append('Study Level')
    rsvp.append('Qualification')
    rsvp.append('Department')

    for col_num in range(len(rsvp)):
        ws.write(row_num, col_num, rsvp[col_num], font_style)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()

    for c in rsvps:

        row_num = row_num + 1
        row = []

        gender,race,nationality,employed,level,dept = '','','','','',''

        if c.student.gender == 1:
            gender = 'Male'
        else:
            gender = 'Female'

        if c.student.race == 1:
            race = 'Black'
        elif c.student.race == 2:
            race='Coloured'
        elif c.student.race == 3:
            race='Asian'
        elif c.student.race == 4:
            race = 'White'

        if c.student.nationality:
            nationality = c.student.nationality.countryName

        if c.student.employed == 1:
            employed = 'Employed'
        else:
            employed = 'Unemployed'

        if c.student.level:
            level = c.student.level.level

        if c.student.department:
            dept = c.student.department.department
    

        row.append(f'{c.student.name} {c.student.surname}')
        row.append(c.student.student_number)
        row.append(c.student.contact_number)
        row.append(c.student.email)
        row.append(gender)
        row.append(race)
        row.append(nationality)
        row.append(employed)
        row.append(level)
        row.append(c.student.qualification)
        row.append(dept)

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response



@login_required()
def event_registration_company_approved(request,pk,rsvp_pk):
    try:
        event_instance = Event.objects.get(id = pk)
        rsvp = EventCompanyRSVP.objects.get(id = rsvp_pk)
        if rsvp.approved == 'Yes':
            rsvp.approved = 'No'
            if event_instance.virtual_spaces.count() > 0:
                check_company_virtual_space = VirtualSpaceBooth.objects.filter(company=rsvp.company,virtual_space=event_instance.virtual_spaces.first())
                if check_company_virtual_space.count() > 0:
                    c = check_company_virtual_space.first()
                    c.delete()
        else:
            rsvp.approved = 'Yes'
            if event_instance.virtual_spaces.count() > 0:
                space = event_instance.virtual_spaces.first()
                check_company_virtual_space = VirtualSpaceBooth.objects.filter(company=rsvp.company,virtual_space=space)
                if check_company_virtual_space.count() == 0:
                    c = VirtualSpaceBooth(virtual_space = space,company = rsvp.company,booth_type="Company",name=rsvp.company.company_name,logo=rsvp.company.logo,website=rsvp.company.website,description='',linked_in=rsvp.company.linked_in,facebook = rsvp.company.facebook,twitter=rsvp.company.twitter,email=rsvp.company.company_email,telephone=rsvp.company.telephone,address=rsvp.company.address)
                    c.save()

                    for contact in rsvp.company.contacts.all():
                        delegate = VirtualSpaceBoothDelegate(virtual_space_booth = c,first_name =contact.name,last_name=contact.surname,email=contact.email,user = contact.user)
                        delegate.save()
        rsvp.save()

        messages.success(request,"Successfully updated approval status")
    except Exception as e:
        messages.warning(request,str(e))

    if request.user.roles_id == 2:
        return redirect('wil:view_company_rsvps',pk=pk)
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:view_company_rsvps',pk=pk)


@login_required()
def event_registration_company_paid(request,pk,rsvp_pk):
    try:
        event_instance = Event.objects.get(id = pk)
        rsvp = EventCompanyRSVP.objects.get(id = rsvp_pk)
        if rsvp.paid == 'Yes':
            rsvp.paid = 'No'
        else:
            rsvp.paid = 'Yes'
        rsvp.save()

        messages.success(request,"Successfully updated payment")
    except Exception as e:
        messages.warning(request,str(e))

    if request.user.roles_id == 2:
        return redirect('wil:view_company_rsvps',pk=pk)
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:view_company_rsvps',pk=pk)


@login_required()
def event_registration_company_delete(request,pk,rsvp_pk):

    try:
        event_instance = Event.objects.get(id = pk)
        rsvp = EventCompanyRSVP.objects.get(id = rsvp_pk)
        rsvp.delete()
        messages.success(request,"Successfully deleted Company Registration Form")
    except:
        messages.warning(request,"An error has occurred, please try again")

    if request.user.roles_id == 2:
        return redirect('wil:view_company_rsvps',pk=pk)
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:view_company_rsvps',pk=pk)


@login_required()
def event_registration_company_form_view(request,pk):
    rsvp = EventCompanyRSVP.objects.get(id = pk)
    check_reg_form = EventCompanyRSVP.objects.filter(event = rsvp.event, company = rsvp.company).first()
    questions = EventRegistrationFormQuestion.objects.filter(registration_form = check_reg_form.registration_form.id).order_by('question_number')

    return render(request,'events/view_registration_form.html',{'rsvp':rsvp,'check_reg_form':check_reg_form,'questions':questions})


@login_required()
def print_registration_form_pdf(request,pk):

    reg_form = EventCompanyRSVP.objects.get(id = pk)

    buffer = BytesIO()

    registration_form = MyPrint('A4')
    pdf_value = registration_form.print_registration_form(pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{reg_form.company.company_name}.pdf"'

    response.write(pdf_value)
    return response

@login_required()
def print_registrations_pdf(request,pk):

    event = Event.objects.get(id = pk)

    buffer = BytesIO()

    registrations = MyPrintReg('A4')
    pdf_value = registrations.print_registrations(pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{event.title}.pdf"'

    response.write(pdf_value)
    return response


@login_required()
def export_registration_forms_excel(request,pk):

    reg_form = EventCompanyRSVP.objects.filter(event_id = pk)
    event = Event.objects.get(id=pk)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{event.title}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('registrations')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    event_info = []

    event_info.append('Company')
    event_info.append('Contact')
    event_info.append('Email')
    event_info.append('Paid')
    event_info.append('Approved')
    event_info.append('Date')

    for col_num in range(len(event_info)):
        ws.write(row_num, col_num, event_info[col_num], font_style)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()

    for r in reg_form:
        row_num = row_num + 1
        row = []

        contact = r.company.contacts.first()
        try:
            row.append(r.company.company_name)
            row.append(f'{contact.name} {contact.surname}')
            row.append(contact.email)
        except:
            pass
        row.append(r.paid)
        row.append(r.approved)
        row.append(r.created_at.strftime("%m/%d/%Y, %H:%M:%S"))

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@login_required()
def event_add_rsvp(request,pk):
    student_instance = Student.objects.get(user_id = request.user.id)
    event_instance = Event.objects.get(id = pk)
    chckrsvpexists = EventRSVP.objects.filter(student=student_instance,event=event_instance)
    if chckrsvpexists.exists():
        messages.warning(request,"You have already RSVP'd to this event")
    else:
        rsvp = EventRSVP.objects.create(event = event_instance, student = student_instance)
        rsvp.save()
        messages.success(request, 'Successfully added RSVP')

    return redirect('/student/events')

@login_required()
def event_rsvp_ajax(request):
    student_pk = request.GET.get('student_pk', None)
    event_pk = request.GET.get('event_pk', None)
    student_instance = Student.objects.get(id = student_pk)
    event_instance = Event.objects.get(id = event_pk)

    chckrsvpexists = EventRSVP.objects.filter(student=student_instance,event=event_instance)

    if chckrsvpexists.exists():
        try:
            chckrsvpexists.delete()
            if event_instance.virtual_spaces.count() > 0:
                space = event_instance.virtual_spaces.first()
                check_student_exists = VirtualSpaceStudentDelegate.objects.filter(student = student_instance,virtual_space = space)
                if check_student_exists.exists():
                    stud = check_student_exists.first()
                    stud.delete()                
                data = { 'is_successful': True,'msg':'RSVP withdrawn Successfully','task':'removed' }
        except:
            data = { 'is_successful': False }
    else:
        try:
            rsvp = EventRSVP.objects.create(event = event_instance, student = student_instance)
            rsvp.save()
            if event_instance.virtual_spaces.count() > 0:
                space = event_instance.virtual_spaces.first()
                check_student_exists = VirtualSpaceStudentDelegate.objects.filter(student = student_instance,virtual_space = space)
                if check_student_exists.exists():
                    pass
                else:
                    s = VirtualSpaceStudentDelegate(virtual_space = space,student = student_instance,user=request.user)
                    s.save()

            data = { 'is_successful': True,'msg':'Successfully added RSVP, please note that by RSVPing you agree for us to share your CV to potential employers during the recruitment programme','task':'applied' }
        except:
            data = { 'is_successful': False }

    return JsonResponse(data)


@login_required()
def remove_rsvp(request,pk):
    chckrsvpexists = EventRSVP.objects.get(id = pk)
    if chckrsvpexists:
        chckrsvpexists.delete()
        messages.success(request,"Successfully removed RSVP")
    else:
        messages.warning(request, 'An error ocurred, please try again')

    return redirect('/student/events/rsvp')

@login_required()
def event_delete(request,pk):
    try:
        event = Event.objects.get(id=pk)
        event.delete()
        messages.success(request,"Successfully deleted Event")
    except:
        messages.warning(request,"An error has occured, Event not deleted, please try again or contact your administrator")

    if request.user.roles_id == 2:
        return redirect('wil:event_list')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_list')


@login_required()
def event_publish(request,pk):
    try:
        event = Event.objects.get(id=pk)
        if event.published == 'Yes':
            event.published = 'No'
            event.save(update_fields=["published"])
            messages.success(request,"Successfully unpublished event")
        else:
            event.published = 'Yes'
            event.save(update_fields=["published"])
            messages.success(request,"Successfully published event")

    except:
        messages.warning(request,"An error has occured, please try again or contact your administrator")

    if request.user.roles_id == 2:
        return redirect('wil:event_list')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_list')

@login_required()
def event_remove_faculty(request,pk,faculty_id):
    event = Event.objects.get(id = pk)
    faculty = Faculty.objects.get(id = faculty_id)
    try:
        event.faculties.remove(faculty)
        messages.success(request,"Successfully removed faculty")
    except:
        messages.warning(request,"Something wrong happened, faculty was not removed, please try again")

    if request.user.roles_id == 2:
        return redirect('wil:event_list')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_list')


@login_required()
def event_add_faculty(request,pk):
    event = Event.objects.get(id = pk)
    faculty = Faculty.objects.get(id = request.POST['faculty'])
    try:
        event.faculties.add(faculty)
        messages.success(request,"Successfully added faculty")
    except:
        messages.warning(request,"Something wrong happened, faculty was not added, please try again")

    if request.user.roles_id == 2:
        return redirect('wil:event_list')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_list')



class EventTypeList(LoginRequiredMixin,ListView):
    template = 'events/eventtype_list.html'
    model = EventType
    context_object_name = 'types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = EventTypeForm()
        context['form'] = form
        context['config_menu'] = 'active'
        return context


@login_required()
def add_eventtypes(request):
    if request.method == 'POST':
        form = EventTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Event type added successfully')
        else:
            messages.warning(request,form.errors)

    return redirect('psycad:config_eventtypes')


@login_required()
def edit_eventtypes(request,pk):
    if request.method == "POST":
        try:
            type_instance = EventType.objects.get(id = pk)
            if request.POST["task"] == "edit":
                form = EventTypeForm(request.POST,instance = type_instance)
                if form.is_valid():
                    form.save()
                    messages.success(request,'Event type edited successfully')
                else:
                    messages.warning(request,form.errors)

            if request.POST["task"] == "delete":
                type_instance.delete()
                messages.success(request,'Event type deleted successfully')

        except Exception as e:
            messages.warning(request,e.message)

    return redirect('psycad:config_eventtypes')

@login_required()
def event_types_registration_form(request,pk):

    if request.method == "POST":
        event_type = EventType.objects.get(id = pk)

        form = EventRegistrationFormForm(request.POST)
        if form.is_valid():
            regform = form.save(commit = False)
            regform.event_type = event_type
            regform.save()
            messages.success(request,"Successfully added registration form, now let's add some questions")
        else:
            messages.warning(request,form.errors)

    event_type = EventType.objects.get(id = pk)
    types = EventType.objects.all()
    form = EventRegistrationFormForm()

    question_types = QuestionType.objects.all()
    return render(request,'events/event_type_registration_form.html',{'types':question_types,'event_type':event_type,'form':form,'types':types})


@login_required()
def edit_event_types_registration_form(request,pk,form_pk):

    if request.method == "POST":
        regform_instance = EventRegistrationForm.objects.get(id = form_pk)

        form = EventRegistrationFormForm(request.POST,instance=regform_instance)
        if form.is_valid():
            form.save()
            messages.success(request,"Successfully edited registration form, now let's add some questions")
        else:
            messages.warning(request,form.errors)

    return redirect('psycad:event_types_registration_form',pk=pk)

@login_required()
def delete_event_types_registration_form(request,pk,form_pk):

    try:
        regform_instance = EventRegistrationForm.objects.get(id = form_pk)
        ##test if there any forms filled##
        regform_instance.delete()

        messages.success(request,"Successfully deleted registration form")
    except:
        messages.warning(request,"An error has occurred")

    return redirect('psycad:event_types_registration_form',pk=pk)


@login_required()
def duplicate_event_type_registration_form(request,pk,duplicate_form_pk):

    if request.method == "POST":
        event_type = EventType.objects.get(id = request.POST['event_type'])

        form = EventRegistrationFormForm(request.POST)
        if form.is_valid():
            regform = form.save(commit = False)
            regform.event_type = event_type
            regform.save()
            messages.success(request,"Successfully duplicated registration form")

            regform_instance = EventRegistrationForm.objects.get(id = duplicate_form_pk)
            for qn in regform_instance.questions.all():
                q = EventRegistrationFormQuestion(question = qn.question,type = qn.type,choice = qn.choice,registration_form = regform,required = qn.required,question_number = qn.question_number)
                q.save()

            messages.success(request,"Successfully added questions to the registration form")

        else:
            messages.warning(request,form.errors)

    return redirect('psycad:event_types_registration_form',pk=event_type.id)



@login_required()
def registration_form_questions(request,pk,form_pk):

    if request.method == "POST":
        regform = EventRegistrationForm.objects.get(id = form_pk)

        form = EventRegistrationFormQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit = False)
            question.registration_form = regform
            question.type_id = request.POST['type']
            question_number = 1
            check_number = EventRegistrationFormQuestion.objects.filter(registration_form = regform.id).order_by('question_number')
            if check_number.exists():
                last = check_number.last()
                question_number = last.question_number
                question_number = question_number + 1

            question.question_number = question_number
            question.save()
            messages.success(request,"Successfully added question")

            if 'upload_file' in request.FILES:
                form_file = EventRegistrationFormFileQuestionForm(request.POST,request.FILES,instance=question)
                if form_file.is_valid():
                    form_file.save()
                    messages.success(request,'Successfully uploaded file')
                else:
                    messages.wrning(request,form_file.errors)

        else:
            messages.warning(request,form.errors)


    event_type = EventType.objects.get(id = pk)
    regform = EventRegistrationForm.objects.get(id = form_pk)
    questions = EventRegistrationFormQuestion.objects.filter(registration_form = regform.id).order_by('question_number')
    question_types = QuestionType.objects.all()


    return render(request,'events/event_type_registration_form_questions.html',{'event_type':event_type,'regform':regform,'types':question_types,'questions':questions})


@login_required()
def edit_event_types_registration_form_question(request,pk,form_pk,question_pk):

    question = EventRegistrationFormQuestion.objects.get(id = question_pk)
    form = EventRegistrationFormQuestionForm(request.POST,instance = question)
    if form.is_valid():
        question = form.save(commit = False)
        question.type_id = request.POST['type']
        if request.POST['question_number'] != "":
            question.question_number = request.POST['question_number']
        question.save()

        if 'upload_file' in request.FILES:
            form_file = EventRegistrationFormFileQuestionForm(request.POST,request.FILES,instance=question)
            if form_file.is_valid():
                form_file.save()
                messages.success(request,'Successfully uploaded file')
            else:
                messages.wrning(request,form_file.errors)
        messages.success(request,"Successfully edited question")
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:registration_form_questions',pk=pk,form_pk=form_pk)



@login_required()
def delete_registration_form_question(request,pk,form_pk,question_pk):

    try:
        question = EventRegistrationFormQuestion.objects.get(id = question_pk)
        ###check if there are any answers####
        question.delete()
        messages.success(request,"Successfully deleted question")
    except:
            messages.warning(request,"An error has occurred")

    return redirect('psycad:registration_form_questions',pk=pk,form_pk=form_pk)


@login_required()
def send_message_rsvps(request,pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 12:
        event = Event.objects.get(id=pk)
        students = request.POST.getlist('students[]')
        feedback = []
        bcc=[]
        sender=[request.user.email]

        for student in students:
            s = Student.objects.get(id=int(student))
            bcc.append(s.email)
            bcc.append(s.alternate_email)
       
        resp = send_email_student_event_message(bcc,event.title,"Student",request.POST['rsvp_message'],"donotreply@UJCareerWiz.co.za",f'UJCareerWiz Admin',request.POST['subject'])
       
        if resp == 1:
            messages.success(request,'Successfully sent emails')
        else:
            messages.warning(request,'An error has occurred')

        if request.user.roles_id == 2:
            return redirect('wil:view_rsvps', pk = pk)
        elif request.user.roles_id == 10 or request.user.roles_id == 11:
            return redirect('psycad:view_rsvps', pk = pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


class EventAnnouncements(LoginRequiredMixin,ListView):
    template = 'events/announcements_list.html'
    model = Announcements
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AnnouncementsForm()
        context['form'] = form
        context['eve_menu'] = 'active'
        return context


@login_required()
def add_event_announcement(request):
    if request.method == 'POST':
        form = AnnouncementsForm(request.POST)
        if form.is_valid():
            a = form.save(commit = False)
            a.published = 'Yes'
            a.save()
            messages.success(request,'Event announcement added successfully')
        else:
            messages.warning(request,form.errors)

    if request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_announcement_list')


@login_required()
def edit_event_announcement(request,pk):
    if request.method == "POST":
        try:
            type_instance = Announcements.objects.get(id = pk)
            if request.POST["task"] == "edit":
                form = AnnouncementsForm(request.POST,instance = type_instance)
                if form.is_valid():
                    form.save()
                    messages.success(request,'Event announcement edited successfully')
                else:
                    messages.warning(request,form.errors)

            if request.POST["task"] == "delete":
                type_instance.delete()
                messages.success(request,'Event announcement deleted successfully')

        except Exception as e:
            messages.warning(request,e.message)

    if request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_announcement_list')


@login_required()
def event_announcement_publish(request,pk):
    try:
        announcement = Announcements.objects.get(id=pk)
        if announcement.published == 'Yes':
            announcement.published = 'No'
            announcement.save(update_fields=["published"])
            messages.success(request,"Successfully unpublished announcement")
        else:
            announcement.published = 'Yes'
            announcement.save(update_fields=["published"])
            messages.success(request,"Successfully published announcement")

    except:
        messages.warning(request,"An error has occured, please try again or contact your administrator")

    if request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:event_announcement_list')


@login_required()
def report_events(request):

    if request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9  or request.user.roles_id == 1:
        events = Event.objects.all()

        if request.method == 'POST':
            if int(request.POST['type']) > 0:
                events = events.filter(type_id = request.POST['type'])
            if int(request.POST['faculty']) > 0:
                events = events.filter(faculties = request.POST['faculty'])
            if int(request.POST['year']) > 0:
                events = events.filter(created_at__contains = request.POST['year'])

        faculties = Faculty.objects.all()
        types = EventType.objects.all()
        today = datetime.date.today()
        years = []
        year = today.year
        for y in range(2):
            years.append(year)
            year = year - 1

        return render(request,'reports/events.html',{'events':events,'faculties':faculties,'types':types,'years':years,'reports_event_menu':'active'})

    else:
        return redirect('accounts:logout')

@login_required()
def report_view_rsvps(request,pk):

    if request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9  or request.user.roles_id == 1:
        event = Event.objects.get(id = pk)
        rsvps = event.rsvp_students.all()

        if request.method == 'POST':
            if int(request.POST['faculty']) > 0:
                rsvps = rsvps.filter(student__department__faculty_id = request.POST['faculty'])
            if int(request.POST['level']) > 0:
                rsvps = rsvps.filter(student__level_id = request.POST['level'])

        faculties = Faculty.objects.all()
        levels = Level.objects.all()
        return render(request,'reports/events_students.html',{'event':event,'rsvps':rsvps,'faculties':faculties,'reports_event_menu':'active','levels':levels})

    else:
        return redirect('accounts:logout')

@login_required()
def report_view_company_rsvps(request,pk):

    if request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9  or request.user.roles_id == 1:
        event = Event.objects.get(id = pk)
        rsvps = event.companies.all()

        if request.method == 'POST':
            if int(request.POST['approved']) > 0:
                if int(request.POST['approved']) == 1:
                    rsvps = rsvps.filter(approved__exact = 'Yes')
                else:
                    rsvps = rsvps.filter(approved__exact = 'No')
            if int(request.POST['paid']) > 0:
                if int(request.POST['paid']) == 1:
                    rsvps = rsvps.filter(paid__exact = 'Yes')
                else:
                    rsvps = rsvps.filter(paid__exact = 'No')

        return render(request,'reports/events_companies.html',{'event':event,'rsvps':rsvps,'reports_event_menu':'active'})

    else:
        return redirect('accounts:logout')


@login_required()
def report_event_graph(request):

    if request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9  or request.user.roles_id == 1:
        months = []
        month_count = 0
        item_events = []
        ymax_eve_list = []
        event_months_other = []
        months = []
        months_other = []

        item_events_f = []
        ymax_eve_list_f = []
        event_months_other_f = []

        today = datetime.date.today()
        last_day = today

        for m in range (12):
            months.append(last_day)
            last_day = last_day - datetime.timedelta(days=last_day.day)

        last_day = today
        for m in range(6):
            months_other.append(last_day)
            last_day = last_day - datetime.timedelta(days=last_day.day)

        event_types = EventType.objects.all()
        for e in event_types:
            month_count = 0
            event_months_other = []
            for m in months_other:
                event_map = {}
                event_map[month_count] = Event.objects.filter(created_at__startswith=('{}-0{}').format(m.year,m.month),type = e).count()
                event_months_other.append(event_map)
                ymax_eve_list.append(event_map[month_count])

                month_count = month_count + 1

            random_number = random.randint(0,16777215)
            hex_number =format(random_number,'x')
            hex_number = '#'+hex_number

            item_eve = {'title':e.type,'colour':hex_number,'count':event_months_other}
            item_events.append(item_eve)

        month_count = 0
        faculties = Faculty.objects.all()
        for f in faculties:
            month_count = 0
            event_months_other_f = []
            for m in months_other:
                event_map_f = {}
                event_map_f[month_count] = Event.objects.filter(created_at__startswith=('{}-0{}').format(m.year,m.month),faculties = f).count()
                event_months_other_f.append(event_map_f)
                ymax_eve_list_f.append(event_map_f[month_count])

                month_count = month_count + 1

            random_number = random.randint(0,16777215)
            hex_number =format(random_number,'x')
            hex_number = '#'+hex_number

            item_eve_f = {'title':f.faculty,'colour':hex_number,'count':event_months_other_f}
            item_events_f.append(item_eve_f)

        ymax_eve_value = max(ymax_eve_list)
        ymax_eve_value_f = max(ymax_eve_list_f)

        return render(request,'reports/event_graphs.html',{'ymax_eve_value':ymax_eve_value,'ymax_eve_value_f':ymax_eve_value_f,'item_events_f':item_events_f,'item_events':item_events,'months_other':months_other})

    else:
        return redirect('accounts:logout')

@login_required()
def event_add_virtual_space(request,pk):

    event = Event.objects.get(id = pk)
    form = VirtualSpaceForm(request.POST)
    if form.is_valid():
        space = form.save(commit = False)
        space.event = event
        space.user = request.user
        space.save()
        admin_booth = VirtualSpaceBooth(virtual_space = space,booth_type="Admin",name='PSYCAD')
        admin_booth.save()
        delegate = VirtualSpaceBoothDelegate(virtual_space_booth = admin_booth,first_name = request.user.first_name,last_name = request.user.last_name,email = request.user.email, user = request.user)
        delegate.save()
        
        for company in event.companies.all():
            if company.approved == 'Yes':
                c = VirtualSpaceBooth(virtual_space = space,company = company.company,booth_type="Company",name=company.company.company_name,logo=company.company.logo,website=company.company.website,description=company.company.description,linked_in=company.company.linked_in,facebook = company.company.facebook,twitter=company.company.twitter,email=company.company.company_email,telephone=company.company.telephone,address=company.company.address)
                c.save()

                for contact in company.company.contacts.all():
                    delegate = VirtualSpaceBoothDelegate(virtual_space_booth = c,first_name =contact.name,last_name=contact.surname,email=contact.email,user = contact.user)
                    delegate.save()

        for student in event.rsvp_students.all():
            s = VirtualSpaceStudentDelegate(virtual_space = space,student = student.student,user=student.student.user)
            s.save()

        messages.success(request,'Successfully created a virtual space. Click on the virtual space to add rooms and view particpants')
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:event_list')


class EventEmailList(LoginRequiredMixin,ListView):
    template_name = 'events/student_email_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        return  EmailPreferences.objects.filter(events = 'Yes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eve_menu'] = 'active'
        return context


@login_required()
def events_students_messenger_send(request):

    if request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9  or request.user.roles_id == 1:
        students = request.POST.getlist('students[]')
        feedback = []
        bcc=[]

        form = AttachmentFileForm(request.POST)
        if form.is_valid():
            send_email = form.save(commit = False)
            send_email.save()
            if 'attachment' in request.FILES:
                form_file = AttachmentFileFileForm(request.POST,request.FILES,instance=send_email)
                if form_file.is_valid():
                    form_file.save()

        for student in students:
            try:
                s = Student.objects.get(id=int(student))
                bcc.append(s.alternate_email)
                feedback.append({'student_number':s.student_number,'name':s.name,'surname':s.surname,'email':s.email,'contact_number':s.contact_number,'sent':'Yes'})                
            except Exception as e:
                messages.warning(request,str(e))

        if send_email.attachment:
            resp = send_email_general_message(bcc,request.POST['message'],request.POST['subject'],'donotreply@UJCareerWiz.co.za',send_email.attachment.path)
        else:
            resp = send_email_general_message(bcc,request.POST['message'],request.POST['subject'],'donotreply@UJCareerWiz.co.za')
        print(resp)
        messages.success(request,'Successfully sent email')
        
        return redirect('psycad:event_emails')
    else:
        return redirect('accounts:logout')


@login_required()
def events_students_messenger_send_all(request):

    if request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9  or request.user.roles_id == 1:
        students = request.POST.getlist('students[]')
        feedback = []
        bcc=[]

        form = AttachmentFileForm(request.POST)
        if form.is_valid():
            send_email = form.save(commit = False)
            send_email.save()
            if 'attachment' in request.FILES:
                form_file = AttachmentFileFileForm(request.POST,request.FILES,instance=send_email)
                if form_file.is_valid():
                    form_file.save()

        students = EmailPreferences.objects.filter(events = 'Yes')

        for stud in students:
            try:
                s = stud.student
                bcc.append(s.alternate_email)
                feedback.append({'student_number':s.student_number,'name':s.name,'surname':s.surname,'email':s.email,'contact_number':s.contact_number,'sent':'Yes'})                
            except Exception as e:
                messages.warning(request,str(e))

        if send_email.attachment:
            resp = send_email_general_message(bcc,request.POST['message'],request.POST['subject'],'donotreply@UJCareerWiz.co.za',send_email.attachment.path)
        else:
            resp = send_email_general_message(bcc,request.POST['message'],request.POST['subject'],'donotreply@UJCareerWiz.co.za')
        print(resp)
        messages.success(request,'Successfully sent email')
        
        return redirect('psycad:event_emails')
    else:
        return redirect('accounts:logout')