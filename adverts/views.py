from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse,HttpResponse
import datetime
import os
from datetime import date
import csv
import xlwt
import openpyxl
from io import BytesIO
from openpyxl.chart import BubbleChart, Reference, Series, BarChart, LineChart
from openpyxl.styles import Font, Color


from .models import Advert, Favourite, Selection,Type,Announcements,TypePrices
from .forms import AdvertCreateForm,AdvertDocumentForm,MentorAdvertCreateForm,AdvertTypeForm,AnnouncementsForm,TypePricesForm
from students.models import Student,EmailPreferences
from django_nursing.email_functions import send_email_advert_apporved,send_email_advert_notification,send_email_advert_updated_notification,sendgrid_student_advert,sendgrid_student_advert_reminder
from .print_advert import MyPrintAdvert,PdfCreatorAdvert

# Create your views here.

def send_mass_email(subject,msg,receipients,sender):
    email = EmailMessage(
        subject,
        msg,
        'info@wilms.co.za',
        to=sender,
        bcc=receipients,
        reply_to=sender,
        headers={'Message-ID': 'wilms'},
    )

    return email.send(fail_silently=False)

def send_single_email(subject,msg,receipient,sender):
    email = EmailMessage(
        subject,
        msg,
        'info@wilms.co.za',
        to=receipient,
        reply_to=sender,
        headers={'Message-ID': 'wilms'},
    )

    return email.send(fail_silently=False)


class AdvertTypeList(LoginRequiredMixin,ListView):
    template = 'adverts/advert_type_list.html'
    model = Type
    context_object_name = 'types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AdvertTypeForm()
        context['form'] = form
        context['adv_menu'] = 'active'
        return context


@login_required()
def add_adverttype(request):
    if request.method == 'POST':
        form = AdvertTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Advert type added successfully')
        else:
            messages.warning(request,form.errors)

    return redirect('psycad:config_adverttypes')


@login_required()
def edit_adverttype(request,pk):
    if request.method == "POST":
        try:
            type_instance = Type.objects.get(id = pk)
            if request.POST["task"] == "edit":
                form = AdvertTypeForm(request.POST,instance = type_instance)
                if form.is_valid():
                    form.save()
                    messages.success(request,'Advert type edited successfully')
                else:
                    messages.warning(request,form.errors)

            if request.POST["task"] == "delete":
                type_instance.delete()
                messages.success(request,'Advert type deleted successfully')

        except Exception as e:
            messages.warning(request,str(e))

    return redirect('psycad:config_adverttypes')


@login_required()
def view_type_payments(request,pk):
    type = Type.objects.get(id = pk)
    form = TypePricesForm()
    return render(request,'adverts/type_payment_list.html',{'type':type,'adv_menu':'active','form':form})

@login_required()
def add_advert_type_payment(request,pk):
    type = Type.objects.get(id = pk)
    if request.method == 'POST':
        form = TypePricesForm(request.POST)
        if form.is_valid():
            payment = form.save(commit = False)
            payment.type = type
            payment.user = request.user
            payment.save()
            messages.success(request,'Payment added successfully')
        else:
            messages.warning(request,form.errors)

    return redirect('psycad:config_advert_type_payment',pk=pk)


@login_required()
def edit_advert_type_payment(request,pk,payment_pk):
    if request.method == "POST":
        try:
            payment_instance = TypePrices.objects.get(id = payment_pk)
            form = TypePricesForm(request.POST,instance = payment_instance)
            if form.is_valid():
                form.save()
                messages.success(request,'Payment edited successfully')
            else:
                messages.warning(request,form.errors)

        except Exception as e:
            messages.warning(request,str(e))

    return redirect('psycad:config_advert_type_payment',pk=pk)


@login_required()
def delete_advert_type_payment(request,pk,payment_pk):
    try:
        payment_instance = TypePrices.objects.get(id = payment_pk)
        payment_instance.delete()
        messages.success(request,'Payment deleted successfully')
    except Exception as e:
        messages.warning(request,str(e))

    return redirect('psycad:config_advert_type_payment',pk=pk)


class AdvertList(LoginRequiredMixin,ListView):
    '''
    Students advert list CBV
    '''
    template_name = 'adverts/list.html'
    context_object_name = 'adverts'

    def get_queryset(self):
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        dept_adverts =  StudentUser.department.adverts.filter(publish__exact='Yes',cut_off_date__gte = datetime.date.today(),post_date__lte = datetime.date.today())
        adverts = []

        for advert in dept_adverts:

            ad = {'advert':advert}

            applied = Favourite.objects.filter(advert = advert, student = StudentUser).exists()
            if applied:
                ad['applied'] = True
            else:
                ad['applied'] = False

            adverts.append(ad)

        return adverts

    def get_context_data(self, **kwargs):
        context = super(AdvertList, self).get_context_data(**kwargs)
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        context['adverts_menu'] = 'active'
        context['title'] = f'Jobs targeted for {StudentUser.department.department} students'
        return context

class AdvertListAll(LoginRequiredMixin,ListView):
    '''
    Students advert list CBV
    '''
    template_name = 'adverts/list.html'
    context_object_name = 'adverts'

    def get_queryset(self):
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        dept_adverts =  Advert.objects.filter(publish__exact='Yes',cut_off_date__gte = datetime.date.today(),post_date__lte = datetime.date.today())
        adverts = []

        for advert in dept_adverts:

            ad = {'advert':advert}

            applied = Favourite.objects.filter(advert = advert, student = StudentUser).exists()
            if applied:
                ad['applied'] = True
            else:
                ad['applied'] = False

            adverts.append(ad)


        return adverts

    def get_context_data(self, **kwargs):
        context = super(AdvertListAll, self).get_context_data(**kwargs)
        context['title'] = "All Jobs posted on UJCareerWiz"
        context['adverts_menu'] = 'active'
        return context

class AdvertListApplied(LoginRequiredMixin,ListView):
    '''
    Students advert list Applied CBV
    '''
    template_name = 'adverts/list_applied.html'
    context_object_name = 'adverts'

    def get_queryset(self):
        StudentUser = Student.objects.get(user_id = self.request.user.id)
        return  Favourite.objects.filter(student = StudentUser,advert__publish__exact='Yes')


    def get_context_data(self, **kwargs):
        context = super(AdvertListApplied, self).get_context_data(**kwargs)
        context['adverts_menu'] = 'active'
        return context

class AdvertLectList(LoginRequiredMixin,ListView):
    '''
    Lecturer advert list CBV
    '''
    template_name = 'adverts/list_lecturer.html'
    context_object_name = 'adverts'

    def get_queryset(self):
        LecturerUser = Lecturer.objects.get(user_id = self.request.user.id)
        return LecturerUser.department.adverts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['adv_menu'] = 'active'
        context['faculties'] = Faculty.objects.all()
        return context

class AdvertAllList(LoginRequiredMixin,ListView):
    '''
    Lecturer advert list CBV
    '''
    template_name = 'adverts/list_all.html'
    context_object_name = 'adverts'
    model = Advert

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = form = AdvertDocumentForm()
        context['adv_menu'] = 'active'
        context['form'] = form
        context['active'] = False
        context['faculties'] = Faculty.objects.all()
        return context


class AdvertActiveList(LoginRequiredMixin,ListView):
    '''
    Lecturer advert active list CBV
    '''
    template_name = 'adverts/list_all.html'
    context_object_name = 'adverts'

    def get_queryset(self):        
        return Advert.objects.filter(cut_off_date__gte = datetime.date.today())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = form = AdvertDocumentForm()
        context['adv_menu'] = 'active'
        context['form'] = form
        context['active'] = True
        context['faculties'] = Faculty.objects.all()
        return context


class AdminAdvertAllList(LoginRequiredMixin,ListView):
    '''
    Lecturer advert list CBV
    '''
    template_name = 'adverts/list_all_admin.html'
    context_object_name = 'adverts'
    model = Advert

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = form = AdvertDocumentForm()
        context['adv_menu'] = 'active'
        context['form'] = form
        context['faculties'] = Faculty.objects.all()
        return context


class AdvertDetailView(LoginRequiredMixin,DetailView):
    template_name = 'adverts/detail.html'
    model = Advert

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['adv_menu'] = 'active'
        return context

class AdvertCreateView(LoginRequiredMixin,CreateView):
    template_name = 'adverts/create.html'
    form_class = AdvertCreateForm

    success_message = "Advert was created successfully."
    error_message = "Unfortunately something went wrong, please try again"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        company = Company.objects.get(id = self.request.POST['company'])
        self.object.company_id = self.request.POST['company']
        self.object.company_name = company.company_name
        
        self.object.cut_off_date = self.request.POST['cut_off_date']
        self.object.post_date = self.request.POST['post_date']

        if int(self.request.POST['level']) > 0:
            self.object.level_id = self.request.POST['level']

        if int(self.request.POST['degree']) > 0:
            self.object.degree_id = self.request.POST['degree']

        documents_required_list = self.request.POST.getlist('documents[]')
        separator = ', '
        documents_required = separator.join(documents_required_list)

        if 'other_document' in self.request.POST:
            documents_required = documents_required + ", " + self.request.POST['other_document']

        self.object.documents = documents_required

        if 'type_price' in self.request.POST:
            self.object.type_price_id = self.request.POST['type_price']

        if 'link' in self.request.POST:
            self.object.link = self.request.POST['link']

        self.object.save()

        depts = self.request.POST.getlist('departments[]')

        if 'all' in depts:
            departments = Department.objects.all()
            self.object.departments.add(*departments)
        else:
            for dept in depts:
                department = Department.objects.get(id = dept)
                self.object.departments.add(department)

        self.object.save()

        if 'file' in self.request.FILES:
            file_form = AdvertDocumentForm(self.request.POST,self.request.FILES,instance=self.object)
            if file_form.is_valid():
                file_form.save()

        if self.request.user.roles_id == 2:
            return redirect('wil:advert_list_active')
        elif self.request.user.roles_id == 10 or self.request.user.roles_id == 11:
            return redirect('psycad:advert_list_active')

    def get_context_data(self, **kwargs):
        context = super(AdvertCreateView, self).get_context_data(**kwargs)
        departments = Department.objects.all().order_by('department')
        context['adv_menu'] = 'active'
        context['industries'] = Industry.objects.all().order_by('industry')
        context['companies'] = Company.objects.all().order_by('company_name')
        context['faculties'] = Faculty.objects.all()
        context['degrees'] = DegreeChoices.objects.all()
        context['levels'] = Level.objects.all()
        context['types'] = Type.objects.all()
        context['regions'] = Region.objects.all()
        return context


@login_required()
def save_advert(request):
    form = AdvertCreateForm(request.POST)
    if form.is_valid():
        advert = form.save(commit = False)
        advert.user = request.user
        company = Company.objects.get(id = request.POST['company'])
        advert.company_id = request.POST['company']
        advert.company_name = company.company_name
        
        advert.cut_off_date = request.POST['cut_off_date']
        advert.post_date = request.POST['post_date']

        if int(request.POST['level']) > 0:
            advert.level_id = request.POST['level']

        if int(request.POST['degree']) > 0:
            advert.degree_id = request.POST['degree']

        documents_required_list = request.POST.getlist('documents[]')
        separator = ', '
        documents_required = separator.join(documents_required_list)

        if 'other_document' in request.POST:
            documents_required = documents_required + ", " + request.POST['other_document']

        advert.documents = documents_required

        if 'type_price' in request.POST:
            advert.type_price_id = request.POST['type_price']

        if 'link' in request.POST:
            advert.link = request.POST['link']

        advert.save()

        depts = request.POST.getlist('departments[]')

        if 'all' in depts:
            departments = Department.objects.all()
            advert.departments.add(*departments)
        else:
            for dept in depts:
                department = Department.objects.get(id = dept)
                advert.departments.add(department)

        advert.save()

        if 'file' in request.FILES:
            file_form = AdvertDocumentForm(request.POST,request.FILES,instance=advert)
            if file_form.is_valid():
                file_form.save()

        messages.success(request,'Successfully added advert')
        if request.user.roles_id == 2:
            return redirect('wil:advert_list_active')
        elif request.user.roles_id == 10 or request.user.roles_id == 11:
            return redirect('psycad:advert_list_active')
    else:
        messages.warning(request,form.errors)

    if request.user.roles_id == 2:
        return redirect('wil:advert_create')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_create')
    


class AdvertUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'adverts/edit.html'
    model = Advert
    context_object_name = 'advert'
    pk_url_kwarg = 'pk'
    fields = ('company_name','position','description','type','paid','requirements','industry','apply','region','address','contract','publish')

    success_message = "Advert was edited successfully."
    error_message = "Unfortunately something went wrong, please try again"

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.cut_off_date = self.request.POST['cut_off_date']
        self.object.post_date = self.request.POST['post_date']

        if int(self.request.POST['level']) > 0:
            self.object.level_id = self.request.POST['level']

        if int(self.request.POST['degree']) > 0:
            self.object.degree_id = self.request.POST['degree']

        if 'documents' in self.request.POST:
            self.object.documents = self.request.POST['documents']

        if 'link' in self.request.POST:
                self.object.link = self.request.POST['link']

        if 'type_price' in self.request.POST:
            if int(self.request.POST['type_price']) > 0:
                self.object.type_price_id = self.request.POST['type_price']

        self.object.save()

        messages.success(self.request,'Successfully edited Advert')

        if self.request.user.roles_id == 2:
            return redirect('wil:advert_list')
        elif self.request.user.roles_id == 10 or self.request.user.roles_id == 11:
            return redirect('psycad:advert_list')

    def get_context_data(self, **kwargs):

        context = super(AdvertUpdateView, self).get_context_data(**kwargs)
        context['adv_menu'] = 'active'
        context['industries'] = Industry.objects.all().order_by('industry')
        context['degrees'] = DegreeChoices.objects.all()
        context['levels'] = Level.objects.all()
        context['types'] = Type.objects.all()
        context['regions'] = Region.objects.all()
        advert = Advert.objects.get(id = self.kwargs['pk'])
        context['pricing'] = TypePrices.objects.filter(type_id = advert.type_id)
        return context

@login_required()
def edit_advert_coordinator(request,pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9:
        advert_instance = Advert.objects.get(id = pk)
        form = AdvertCreateForm(request.POST,instance=advert_instance)
        if form.is_valid():
            advert = form.save(commit=False)
            advert.cut_off_date = request.POST['cut_off_date']
            advert.post_date = request.POST['post_date']

            if int(request.POST['level']) > 0:
                advert.level_id = request.POST['level']

            if int(request.POST['degree']) > 0:
                advert.degree_id = request.POST['degree']

            if 'documents' in request.POST:
                advert.documents = request.POST['documents']

            if 'link' in request.POST:
                advert.link = request.POST['link']

            if 'type_price' in request.POST:
                if int(request.POST['type_price']) > 0:
                    advert.type_price_id = request.POST['type_price']
            messages.success(request,'Successfully edited Advert')
            advert.save()
        else:
            messages.warning(request,form.errors)

        if request.user.roles_id == 2:
            return redirect('wil:advert_list_active')
        elif request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 9:
            return redirect('psycad:advert_list_active')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')



@login_required()
def view_adverts_as(request):
    adverts = Advert.objects.filter(cut_off_date__gt = datetime.date.today())
    return render(request,'adverts/as_student.html',{'adverts':adverts,'view_as':'student'})


@login_required()
def advert_delete(request,pk):
    try:
        advert = Advert.objects.get(id=pk)
        advert.delete()
        messages.success(request,"Successfully deleted advert")
    except:
        messages.warning(request,"An error has occured, advert not deleted, please try again or contact your administrator")

    if request.user.roles_id == 2:
        return redirect('wil:advert_list_active')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_list_active')
    elif request.user.roles_id == 12:
        return redirect('mentor:advert_list')
    elif request.user.roles_id == 3:
        return redirect('contact:advert_list')


@login_required()
def advert_publish(request,pk):
    try:
        advert = Advert.objects.get(id=pk)
        if advert.publish == 'Yes':
            advert.publish = 'No'
            advert.save(update_fields=["publish"])
            messages.success(request,"Successfully unpublished advert")
        else:
            advert.publish = 'Yes'
            advert.save(update_fields=["publish"])
            messages.success(request,"Successfully published advert")

            company_rep = Responsibilities.objects.filter(responsibility__exact = 'company_rep').first()

            from_name = f'{company_rep.user.first_name} {company_rep.user.last_name}'
            to_email = advert.user.email
            name = f'{advert.user.first_name} {advert.user.last_name}'
            position = advert.position
            from_email = company_rep.user.email

            send_email_advert_apporved(from_name,to_email,name,position,from_email)

            departments = advert.departments.all()
            to = [To('donotreply@UJCareerWiz.co.za', 'UJCareerWiz Admin', p=0)]
            bcc_emails = [Bcc(request.user.email,request.user.first_name, p=0)]
            students = []

            for department in departments:
                for student in department.students.all():
                    if student.user is not None:                                              
                        bcc_emails.append(Bcc(student.alternate_email, student.name, p=0))
                        bcc_emails.append(Bcc(student.email, student.name, p=0))
                        #bcc_emails.append(Bcc("mmuwanguzi@gmail.com","Mark", p=0))
                        students.append(student)


            message_sent,error = sendgrid_student_advert(to,bcc_emails,advert.company.company_name,advert.position)
       
            messages.success(request,f'An email has been sent to {len(students)} student(s) informing them of this job opportunity.  {error}')
            return render(request,'adverts/list_email_summary.html',{'students':students,'advert':advert})
            

    except Exception as e:
        messages.warning(request,f"An error has occured, please try again or contact your administrator. Error message: {str(e)}")

    if request.user.roles_id == 2:
        return redirect('wil:advert_list_active')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_list_active')
    elif request.user.roles_id == 12:
        return redirect('mentor:advert_list')
    elif request.user.roles_id == 3:
        return redirect('contact:advert_list')


@login_required()
def advert_send_email(request,pk):
    try:
        advert = Advert.objects.get(id=pk)
        if advert.publish == 'Yes':            
            departments = advert.departments.all()
            to = To('donotreply@UJCareerWiz.co.za')
            bcc_emails = [Bcc(request.user.email,request.user.first_name, p=0)]
            students = []
            for department in departments:
                for student in department.students.all():
                    if student.user is not None:                                              
                        bcc_emails.append(Bcc(student.alternate_email, student.name, p=0))
                        bcc_emails.append(Bcc(student.email, student.name, p=0))
                        #bcc_emails.append(Bcc('mmuwanguzi@gmail.com'))
                        #to = To(student.email)
                        students.append(student)

            size_of_list = len(students)
            number_of_separations = size_of_list // 990
            for x in range(0,number_of_separations):
                if x == 0:
                    begin = 0
                    end = 990

                message_sent,error = sendgrid_student_advert_reminder(to,bcc_emails[begin:end],advert.company.company_name,advert.position,'UJ')
                begin = end
                end = begin + 990


            #message_sent,error = sendgrid_student_advert_reminder(to,bcc_emails[0:900],advert.company.company_name,advert.position,'UJ')   
            #message_sent,error = sendgrid_student_advert_reminder(to,bcc_emails[900:],advert.company.company_name,advert.position,'UJ')                      
            messages.success(request,f'An email has been sent to {len(students)} student(s) informing them of this job opportunity. {error}')
            return render(request,'adverts/list_email_summary.html',{'students':students,'advert':advert})
          
        else:
            messages.warning(request,'This advert is not published, no emails sent to students')
            if request.user.roles_id == 2:
                return redirect('wil:advert_list_active')
            elif request.user.roles_id == 10 or request.user.roles_id == 11:
                return redirect('psycad:advert_list_active')
            elif request.user.roles_id == 12:
                return redirect('mentor:advert_list')
            elif request.user.roles_id == 3:
                return redirect('contact:advert_list')
    except Exception as e:
        messages.warning(request,f"An error has occured, please try again or contact your administrator. Error message: {str(e)}")

    if request.user.roles_id == 2:
        return redirect('wil:advert_list_active')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_list_active')
    elif request.user.roles_id == 12:
        return redirect('mentor:advert_list')
    elif request.user.roles_id == 3:
        return redirect('contact:advert_list')


@login_required()
def advert_publish_dashboard(request,pk):
    try:
        advert = Advert.objects.get(id=pk)
        if advert.publish == 'Yes':
            advert.publish = 'No'
            advert.save(update_fields=["publish"])
            messages.success(request,"Successfully unpublished advert")
        else:
            advert.publish = 'Yes'
            advert.save(update_fields=["publish"])
            messages.success(request,"Successfully published advert")

            company_rep = Responsibilities.objects.filter(responsibility__exact = 'company_rep').first()

            from_name = f'{company_rep.user.first_name} {company_rep.user.last_name}'
            to = advert.user.email
            name = f'{advert.user.first_name} {advert.user.last_name}'
            position = advert.position
            from_email = company_rep.user.email

            send_email_advert_apporved(from_name,to,name,position,from_email)

    except:
        messages.warning(request,"An error has occured, please try again or contact your administrator")

    return redirect('psycad:dashboard')


@login_required()
def advert_remove_department(request,pk,department_id):
    try:
        advert = Advert.objects.get(id=pk)
        department = Department.objects.get(id = department_id)
        advert.departments.remove(department)
        messages.success(request,"Successfully removed department from advert")
    except:
        messages.warning(request,"An error has occured, please try again or contact your administrator")

    if request.user.roles_id == 2:
        return redirect('wil:advert_list_active')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_list_active')
    elif request.user.roles_id == 12:
        return redirect('mentor:advert_list')
    elif request.user.roles_id == 3:
        return redirect('contact:advert_list')

@login_required()
def advert_add_department(request,pk):
    try:
        advert = Advert.objects.get(id=pk)
        department = Department.objects.get(id = request.POST['department'])
        advert.departments.add(department)
        messages.success(request,"Successfully added department to advert")
    except:
        messages.warning(request,"An error has occured, please try again or contact your administrator")

    if request.user.roles_id == 2:
        return redirect('wil:advert_list_active')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_list_active')
    elif request.user.roles_id == 12:
        return redirect('mentor:advert_list')
    elif request.user.roles_id == 3:
        return redirect('contact:advert_list')



@login_required()
def add_advert_file(request,pk):
    advert_instance = Advert.objects.get(id = pk)
    form = AdvertDocumentForm(request.POST, request.FILES, instance = advert_instance)
    if form.is_valid():
        form.save()
        messages.success(request,'Successfully uploaded file')
    else:
        messages.warning(request,form.errors)

    if request.user.roles_id == 2:
        return redirect('wil:advert_list_active')
    elif request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_list_active')
    elif request.user.roles_id == 12:
        return redirect('mentor:advert_list')
    elif request.user.roles_id == 3:
        return redirect('contact:advert_list')


"""
Mentors advert classes and functions
"""

class Mentor_AdvertCreateView(LoginRequiredMixin,CreateView):
    template_name = 'adverts/create_mentor.html'
    form_class = MentorAdvertCreateForm

    success_message = "Thank you for posting your opportunity, it will be approved in due course"
    error_message = "Unfortunately something went wrong, please try again"

    def form_valid(self, form):
        MentorUser = Mentor.objects.get(user_id = self.request.user.id)
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.company = MentorUser.company
        self.object.company_name = MentorUser.company.company_name
        self.object.cut_off_date = self.request.POST['cut_off_date']
        self.object.save()

        #notification = Notification.objects.create(notification = 'New Advert', title = self.object.title, type_id = self.object.id, type = 'ADVERT')
        #notification.save()

        depts = self.request.POST.getlist('departments[]')

        for dept in depts:
            department = Department.objects.get(id = dept)
            self.object.departments.add(department)

        self.object.save()

        company_rep = Responsibilities.objects.filter(responsibility__exact = 'company_rep').first()

        to = company_rep.user.email
        name = company_rep.user.first_name
        company = MentorUser.company.company_name
        contact = f'{MentorUser.name} {MentorUser.surname}'
        position = self.object.position

        send_email_advert_notification(to,name,company,contact,position)

        messages.success(self.request,'Thank you for posting your opportunity, it will be approved in due course')

        return redirect('mentor:advert_list')

    def get_context_data(self, **kwargs):
        context = super(Mentor_AdvertCreateView, self).get_context_data(**kwargs)
        faculties = Faculty.objects.all().order_by('faculty')
        context['adv_menu'] = 'active'
        context['faculties'] = faculties
        context['announcements'] = Announcements.objects.filter(published__exact = 'Yes')
        return context

def ajax_type_payments(request):
    id_type = request.GET.get('id_type', None)

    type = Type.objects.get(id = id_type)
    data = []
    for payment in type.prices.all():
        data.append({'id':payment.id,'period':f'{payment.period} - {payment.price}'})

    return JsonResponse(list(data), safe=False)

class ContactAdvertCreateView(LoginRequiredMixin,CreateView):
    template_name = 'adverts/create_mentor.html'
    form_class = MentorAdvertCreateForm

    success_message = "Advert was created successfully."
    error_message = "Unfortunately something went wrong, please try again"

    def form_valid(self, form):
        contact = CompanyContacts.objects.get(user_id = self.request.user.id)
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.company = contact.company
        self.object.company_name = contact.company.company_name
        self.object.cut_off_date = self.request.POST['cut_off_date']
        self.object.post_date = self.request.POST['post_date']

        if int(self.request.POST['level']) > 0:
            self.object.level_id = self.request.POST['level']

        if int(self.request.POST['degree']) > 0:
            self.object.degree_id = self.request.POST['degree']

        documents_required_list = self.request.POST.getlist('documents[]')
        separator = ', '
        documents_required = separator.join(documents_required_list)

        if 'other_document' in self.request.POST:
            documents_required = documents_required + ", " + self.request.POST['other_document']

        self.object.documents = documents_required

        if 'type_price' in self.request.POST:
            self.object.type_price_id = self.request.POST['type_price']

        if 'link' in self.request.POST:
            self.object.link = self.request.POST['link']

        self.object.save()

        depts = self.request.POST.getlist('departments[]')

        if 'all' in depts:
            departments = Department.objects.all()
            self.object.departments.add(*departments)
        else:
            for dept in depts:
                department = Department.objects.get(id = dept)
                self.object.departments.add(department)

        self.object.save()

        if 'file' in self.request.FILES:
            file_form = AdvertDocumentForm(self.request.POST,self.request.FILES,instance=self.object)
            if file_form.is_valid():
                file_form.save()

        company_rep = Responsibilities.objects.filter(responsibility__exact = 'company_rep').first()

        from_email = 'donotreply@ujcareerwiz.co.za'
        to = company_rep.user.email
        name = company_rep.user.first_name
        company = contact.company.company_name
        contact_name = f'{contact.name} {contact.surname}'
        position = self.object.position

        send_email_advert_notification(to,name,company,contact_name,position)

        messages.success(self.request,'Thank you for posting your opportunity, it will be approved in due course')

        return redirect('contact:advert_list')

    def get_context_data(self, **kwargs):
        context = super(ContactAdvertCreateView, self).get_context_data(**kwargs)
        faculties = Faculty.objects.all().order_by('faculty')
        context['adv_menu'] = 'active'
        context['faculties'] = faculties
        context['announcements'] = Announcements.objects.filter(published__exact = 'Yes')
        context['degrees'] = DegreeChoices.objects.all()
        context['levels'] = Level.objects.all()
        context['types'] = Type.objects.all()
        context['industries'] = Industry.objects.all().order_by('industry')
        return context


class Mentor_AdvertList(LoginRequiredMixin,ListView):
    '''
    Mentor  advert list CBV
    '''
    template_name = 'adverts/list_mentor.html'
    context_object_name = 'adverts'

    def get_queryset(self):
        MentorUser = Mentor.objects.get(user_id = self.request.user.id)
        return Advert.objects.filter(company = MentorUser.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = form = AdvertDocumentForm()
        faculties = Faculty.objects.all().order_by('faculty')
        context['faculties'] = faculties
        context['form'] = form
        context['adv_menu'] = 'active'
        context['announcements'] = Announcements.objects.filter(published__exact = 'Yes')
        context['industries'] = Industry.objects.all().order_by('industry')
        context['degrees'] = DegreeChoices.objects.all()
        context['levels'] = Level.objects.all()
        context['types'] = Type.objects.all()
        return context


class ContactAdvertList(LoginRequiredMixin,ListView):
    '''
    Mentor  advert list CBV
    '''
    template_name = 'adverts/list_mentor.html'
    context_object_name = 'adverts'

    def get_queryset(self):
        contact = CompanyContacts.objects.get(user_id = self.request.user.id)
        return Advert.objects.filter(company = contact.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = form = AdvertDocumentForm()
        faculties = Faculty.objects.all().order_by('faculty')
        context['currentDate'] = date.today()
        context['faculties'] = faculties
        context['form'] = form
        context['adv_menu'] = 'active'
        context['announcements'] = Announcements.objects.filter(published__exact = 'Yes')
        return context


class Mentor_AdvertUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'adverts/edit_mentor.html'
    model = Advert
    context_object_name = 'advert'
    pk_url_kwarg = 'pk'
    fields = ('position','description','type','paid','requirements','industry','apply','region','address','contract')

    success_message = "Advert was edited successfully."
    error_message = "Unfortunately something went wrong, please try again"

    def form_valid(self, form):
        advert_old = Advert.objects.get(id = self.object.id)
        self.object = form.save(commit=False)
        self.user = self.request.user
        self.object.cut_off_date = self.request.POST['cut_off_date']
        self.object.post_date = self.request.POST['post_date']

        if int(self.request.POST['level']) > 0:
            self.object.level_id = self.request.POST['level']

        if int(self.request.POST['degree']) > 0:
            self.object.degree_id = self.request.POST['degree']

        if 'documents' in self.request.POST:
            self.object.documents = self.request.POST['documents']

        if 'link' in self.request.POST:
            self.object.link = self.request.POST['link']

        if 'type_price' in self.request.POST:
            if int(self.request.POST['type_price']) > 0:
                self.object.type_price_id = self.request.POST['type_price']

        self.object.save()

        advert_new = self.object
               
        messages.success(self.request,'Successfully edited Advert')

        if self.request.user.roles_id == 12:
            return redirect('mentor:advert_list')
        elif self.request.user.roles_id == 3:
            return redirect('contact:advert_list')

    def get_context_data(self, **kwargs):
        context = super(Mentor_AdvertUpdateView, self).get_context_data(**kwargs)
        context['adv_menu'] = 'active'
        context['announcements'] = Announcements.objects.filter(published__exact = 'Yes')
        context['industries'] = Industry.objects.all().order_by('industry')
        context['degrees'] = DegreeChoices.objects.all()
        context['levels'] = Level.objects.all()
        context['types'] = Type.objects.all()
        context['regions'] = Region.objects.all()
        advert = Advert.objects.get(id = self.kwargs['pk'])
        context['pricing'] = TypePrices.objects.filter(type_id = advert.type_id)
        return context


class Mentor_StudentCVAdvertListView(LoginRequiredMixin,ListView):
    '''
    List of student cvs in the department for the mentor
    '''
    template_name = 'adverts/student_select_advert.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        department = Department.objects.get(id=self.kwargs['dept_pk'])
        students =  Student.objects.filter(department = department).order_by('-created_at')

        studentlist = []
        for s in students:
            if s.cv_check_complete():
                studentlist.append(s)

        return studentlist


    def get_context_data(self, **kwargs):
        context = super(Mentor_StudentCVAdvertListView, self).get_context_data(**kwargs)
        department = Department.objects.get(id=self.kwargs['dept_pk'])
        advert = Advert.objects.get(id=self.kwargs['pk'])
        levels = Level.objects.all()
        regions = Region.objects.all()

        context['levels'] = levels
        context['regions'] = regions
        context['department'] = department
        context['advert'] = advert
        context['adv_menu'] = 'active'
        return context


@login_required()
def students_advert_filter(request,pk,dept_pk):

    if request.user.roles_id == 12 or request.user.roles_id == 3:

        if request.method == "POST":

            if int(request.POST['department']) > 0:
                department_instance = Department.objects.get(id=request.POST['department'])
            else:
                department_instance = Department.objects.get(id=dept_pk)

            page = 1

            student_list = Student.objects.filter(department = department_instance)

            if int(request.POST['gender']) > 0:
                student_list = student_list.filter(gender = request.POST['gender'])
            if int(request.POST['race']) > 0:
                student_list = student_list.filter(race = request.POST['race'])
            if int(request.POST['disability']) > 0:
                student_list = student_list.filter(disability = request.POST['disability'])
            if int(request.POST['level']) > 0:
                student_list = student_list.filter(level_id = request.POST['level'])
            if int(request.POST['region']) > 0:
                student_list = student_list.filter(region_id = request.POST['region'])
            if int(request.POST['employed']) > 0:
                student_list = student_list.filter(employed = request.POST['employed'])

            filter = [request.POST['gender'],request.POST['race'],request.POST['disability'],request.POST['level'],request.POST['region'],request.POST['employed'],str(department_instance.id)]
            filterstr = '-'.join(filter)

            paginator = Paginator(student_list, 20)

            try:
                students = paginator.page(page)
            except PageNotAnInteger:
                students = paginator.page(1)
            except EmptyPage:
                students = paginator.page(paginator.num_pages)

        if request.method == "GET":
            department_instance = Department.objects.get(id=dept_pk)
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')
            student_list = Student.objects.filter(department = department_instance)

            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if int(filter[0]) > 0:
                    student_list = student_list.filter(gender = filter[0])
                if int(filter[1]) > 0:
                    student_list = student_list.filter(race = filter[1])
                if int(filter[2]) > 0:
                    student_list = student_list.filter(disability = filter[2])
                if int(filter[3]) > 0:
                    student_list = student_list.filter(level_id = filter[3])
                if int(filter[4]) > 0:
                    student_list = student_list.filter(region_id = filter[4])
                if int(filter[5]) > 0:
                    student_list = student_list.filter(employed = filter[5])

            paginator = Paginator(student_list, 20)
            try:
                students = paginator.page(page)
            except PageNotAnInteger:
                students = paginator.page(1)
            except EmptyPage:
                students = paginator.page(paginator.num_pages)

        advert = Advert.objects.get(id=pk)
        levels = Level.objects.all()
        regions = Region.objects.all()

        return render(request,'adverts/student_select_advert.html',{'students':students,'filter':filterstr,'department':department_instance,'regions':regions,'levels':levels,'advert':advert,'department_instance':department_instance,'adv_menu':'active'})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def select_students(request,pk,dept_pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 12 or request.user.roles_id == 3:
        advert = Advert.objects.get(id=pk)
        students = request.POST.getlist('students[]')
        feedback = []
        bcc=[]
        sender=[request.user.email]

        for student in students:
            s = Student.objects.get(id=int(student))
            if request.POST['task'] == "message":
                bcc.append(s.email)
            check_selected = Selection.objects.filter(advert=advert,student=s).exists()
            if check_selected == False:
                selected = Selection(advert=advert,student=s,user=request.user)
                selected.save()
                messages.success(request,f'Successfully selected student: {s.name}')

        if request.POST['task'] == "message":
            resp = send_mass_email(request.POST['subject'],request.POST['message'],bcc,sender)

            if resp == 1:
                messages.success(request,'Successfully sent email')
            else:
                messages.warning(request,'An error has occurred')

        if request.user.roles_id == 2:
            return redirect('wil:select_students',pk=pk,dept_pk=dept_pk)
        elif request.user.roles_id == 10 or request.user.roles_id == 11:
            return redirect('psycad:select_students',pk=pk,dept_pk=dept_pk)
        elif request.user.roles_id == 12:
            return redirect('mentor:select_students',pk=pk,dept_pk=dept_pk)
        elif request.user.roles_id == 3:
            return redirect('contact:select_students',pk=pk,dept_pk=dept_pk)


    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def selected_students(request,pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 12 or request.user.roles_id == 3:
        advert = Advert.objects.get(id=pk)
        selectees = Selection.objects.filter(advert = advert)
        return render(request,'adverts/selected_students.html',{'advert':advert,'selectees':selectees,'adv_menu':'active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def remove_selected(request,pk,selectee_id):
    if request.user.roles_id == 2 or request.user.roles_id == 10  or request.user.roles_id == 11 or request.user.roles_id == 12 or request.user.roles_id == 3:
        advert = Advert.objects.get(id=pk)
        try:
            selectee = Selection.objects.get(id = selectee_id)
            selectee.delete()
            messages.success(request,"Successfully removed student from selection")
        except:
            messages.warning(request,'An error occurred, please try again')

        if request.user.roles_id == 2:
            return redirect('wil:selected_students', pk = pk)
        elif request.user.roles_id == 10 or request.user.roles_id == 11:
            return redirect('psycad:selected_students', pk = pk)
        elif request.user.roles_id == 12:
            return redirect('mentor:selected_students', pk = pk)
        elif request.user.roles_id == 3:
            return redirect('contact:selected_students', pk = pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def send_message_selected(request,pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 12  or request.user.roles_id == 3:
        advert = Advert.objects.get(id=pk)
        students = request.POST.getlist('students[]')
        feedback = []
        bcc=[]
        sender=[request.user.email]

        for student in students:
            s = Student.objects.get(id=int(student))
            bcc.append(s.email)

        resp = send_mass_email(request.POST['subject'],request.POST['message'],bcc,sender)

        if resp == 1:
            messages.success(request,'Successfully sent email')
        else:
            messages.warning(request,'An error has occurred')

        if request.user.roles_id == 2:
            return redirect('wil:selected_students', pk = pk)
        elif request.user.roles_id == 10 or request.user.roles_id == 11:
            return redirect('psycad:selected_students', pk = pk)
        elif request.user.roles_id == 12:
            return redirect('mentor:selected_students', pk = pk)
        elif request.user.roles_id == 3:
            return redirect('contact:selected_students', pk = pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def view_applicants(request,pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 12 or request.user.roles_id == 3:
        advert = Advert.objects.get(id=pk)
        applicants = Favourite.objects.filter(advert = advert)

        if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 11:
            return render(request,'adverts/applicants_other.html',{'applicants':applicants,'advert':advert,'adv_menu':'active'})
        elif request.user.roles_id == 12:
                return render(request,'adverts/applicants.html',{'applicants':applicants,'advert':advert,'adv_menu':'active'})
        elif request.user.roles_id == 3:
                return render(request,'adverts/applicants.html',{'applicants':applicants,'advert':advert,'adv_menu':'active'})

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def send_message_applicants(request,pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 12 or request.user.roles_id == 3:
        advert = Advert.objects.get(id=pk)
        students = request.POST.getlist('students[]')
        feedback = []
        bcc=[]
        sender=[request.user.email]

        for student in students:
            s = Student.objects.get(id=int(student))
            bcc.append(s.email)

        #resp = send_mass_email(request.POST['subject'],request.POST['message'],bcc,sender)

        if resp == 1:
            messages.success(request,'Successfully sent email')
        else:
            messages.warning(request,'An error has occurred')

        if request.user.roles_id == 2:
            return redirect('wil:view_applicants', pk = pk)
        elif request.user.roles_id == 10 or request.user.roles_id == 11:
            return redirect('psycad:view_applicants', pk = pk)
        elif request.user.roles_id == 12:
            return redirect('mentor:view_applicants', pk = pk)
        elif request.user.roles_id == 3:
            return redirect('contact:view_applicants', pk = pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def applicants_outcome(request,pk):
    if request.user.roles_id == 2 or request.user.roles_id == 10 or request.user.roles_id == 11 or request.user.roles_id == 12 or request.user.roles_id == 3:
        try:
            applicant = Favourite.objects.get(id = pk)
            applicant.message = request.POST['message']
            applicant.status = request.POST['status']
            applicant.save()
            messages.success(request,'Successfully updated applicants outcome')
        except Exception as e:
            messages.warning(request,'An error has occurred, please fix it and try again: {}'.format(str(e)))

        if request.user.roles_id == 2:
            return redirect('wil:view_applicants', pk = applicant.advert_id)
        elif request.user.roles_id == 10 or request.user.roles_id == 11:
            return redirect('psycad:view_applicants', pk = applicant.advert_id)
        elif request.user.roles_id == 12:
            return redirect('mentor:view_applicants', pk = applicant.advert_id)
        elif request.user.roles_id == 3:
            return redirect('contact:view_applicants', pk = applicant.advert_id)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


#Students functions

@login_required()
def advert_apply(request):
    student_pk = request.GET.get('student_pk', None)
    advert_pk = request.GET.get('advert_pk', None)
    advert = Advert.objects.get(id=advert_pk)
    student = Student.objects.get(id=student_pk)

    check_applied = Favourite.objects.filter(advert=advert,student=student)

    if check_applied.exists():
        try:
            check_applied.delete()
            data = { 'is_successful': True,'msg':'Application withdrawn Successfully, Goodluck','task':'removed' }
        except:
            data = { 'is_successful': False }
    else:
        try:
            apply = Favourite(advert=advert,student=student)
            apply.save()
            data = { 'is_successful': True,'msg':'Successfully applied for post, Goodluck','task':'applied' }
        except:
            data = { 'is_successful': False }

    return JsonResponse(data)

@login_required()
def advert_application_withdraw(request,pk):
    try:
        application = Favourite.objects.get(id=pk)
        application.delete()
        messages.success(request,'Successfully withdrawn application')
    except:
        messages.warning(request,'An error has occurred, please try again')

    return redirect('student:advert_my_applications')


class AdvertAnnouncements(LoginRequiredMixin,ListView):
    template = 'adverts/announcements_list.html'
    model = Announcements
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = AnnouncementsForm()
        context['form'] = form
        context['adv_menu'] = 'active'
        return context


@login_required()
def add_advert_announcement(request):
    if request.method == 'POST':
        form = AnnouncementsForm(request.POST)
        if form.is_valid():
            a = form.save(commit = False)
            a.published = 'Yes'
            a.save()
            messages.success(request,'Advert announcement added successfully')
        else:
            messages.warning(request,form.errors)

    if request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_announcement_list')


@login_required()
def edit_advert_announcement(request,pk):
    if request.method == "POST":
        try:
            type_instance = Announcements.objects.get(id = pk)
            if request.POST["task"] == "edit":
                form = AnnouncementsForm(request.POST,instance = type_instance)
                if form.is_valid():
                    form.save()
                    messages.success(request,'Advert announcement edited successfully')
                else:
                    messages.warning(request,form.errors)

            if request.POST["task"] == "delete":
                type_instance.delete()
                messages.success(request,'Advert announcement deleted successfully')

        except Exception as e:
            messages.warning(request,str(e))

    if request.user.roles_id == 10 or request.user.roles_id == 11:
        return redirect('psycad:advert_announcement_list')


@login_required()
def advert_announcement_publish(request,pk):
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
        return redirect('psycad:advert_announcement_list')


@login_required()
def report_adverts(request):

    adverts = Advert.objects.all()

    if request.method == 'POST':
        if int(request.POST['faculty']) > 0:
            adverts = adverts.filter(departments__faculty_id = request.POST['faculty'])
        if int(request.POST['type']) > 0:
            adverts = adverts.filter(type = request.POST['type'])
        if int(request.POST['year']) > 0:
            adverts = adverts.filter(created_at__contains = request.POST['year'])

    faculties = Faculty.objects.all()
    types = Type.objects.all()
    today = datetime.date.today()
    years = []
    year = today.year
    for y in range(2):
        years.append(year)
        year = year - 1

    return render(request,'reports/adverts.html',{'reports_advert_menu':'active','adverts':adverts,'faculties':faculties,'types':types,'years':years})

@login_required()
def report_view_applicants(request,pk):

    advert = Advert.objects.get(id=pk)
    students = advert.students_favourite.all()

    if request.method == 'POST':

        if int(request.POST['level']) > 0:
            students = students.filter(student__level_id = request.POST['level'])
        if int(request.POST['faculty']) > 0:
            students = students.filter(student__department__faculty_id = request.POST['faculty'])


    faculties = Faculty.objects.all()
    levels = Level.objects.all()

    return render(request,'reports/advert_students.html',{'reports_advert_menu':'active','advert':advert,'faculties':faculties,'levels':levels,'students':students})


@login_required()
def report_adverts_print(request):

    adverts = Advert.objects.order_by('created_at').all()

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="report_adverts.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('adverts')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    ads = []

    ads.append('Company')
    ads.append('Position')
    ads.append('Type of Job')
    ads.append('Region')
    ads.append('Departments')
    ads.append('Number of Applicants')
    ads.append('Date Posted')
    ads.append('Cut off Date')

    for col_num in range(len(ads)):
        ws.write(row_num, col_num, ads[col_num], font_style)

    font_style = xlwt.XFStyle()
    font_style.font.bold = False

    for ad in adverts:

        row_num = row_num + 1
        row = []
        row.append(ad.company.company_name)
        row.append(ad.position)
        if ad.type:
            row.append(ad.type.type)
        else:
            row.append('')

        if ad.region:
            row.append(ad.region.region)
        else:
            row.append('')

        departments = []
        separator = ', '
        for dept in ad.departments.all():
            departments.append(dept.department)
        row.append(separator.join(departments))
        row.append(ad.students_favourite.count())
        row.append(f'{ad.created_at}')
        row.append(f'{ad.cut_off_date}')

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response


@login_required()
def report_advert_graphs(request):
     types = Type.objects.all()

     response = HttpResponse(content_type='text/csv')
     response['Content-Disposition'] = f'attachment; filename="graphs.xlsx"'

     wb = openpyxl.Workbook()

     sheet = wb.active

     # Sheet header, first row
     row_num = 1
     row_max = 1

     font_style = xlwt.XFStyle()
     font_style.font.bold = True

     type_graph = []
     type_graph.append(('Advert Type','Number of Adverts'))
     for t in types:
         type_graph.append((t.type, t.adverts.count()))

     for row in type_graph:
         sheet.append(row)
         row_max = row_max + 1

     data = Reference(sheet, min_col=2, min_row=row_num, max_col=2, max_row=row_max)

     titles = Reference(sheet, min_col=1, min_row=row_num+1, max_row=row_max)
     chart = BarChart()
     chart.title = "Statistics: Advert Types"
     chart.add_data(data=data, titles_from_data=True)
     chart.set_categories(titles)
     chart.y_axis.title = 'Number of Adverts'
     chart.x_axis.title = 'Types of Advert'
     chart.height = 7.5
     chart.width = 20

     # Style the lines

     s2 = chart.series[0]

     #s2 = chart.series[1]
     s2.smooth = True # Make the line smooth

     sheet.add_chart(chart, f"G{row_num}")

     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])

     row_max = row_max + 13
     row_num = row_max

     depts = Department.objects.all()

     depts_graph = []
     depts_graph.append(('Departments','Number of Adverts'))
     for t in depts:
         if t.adverts.count() > 0:
             depts_graph.append((t.department, t.adverts.count()))

     for row in depts_graph:
         sheet.append(row)
         row_max = row_max + 1

     data = Reference(sheet, min_col=2, min_row=row_num, max_col=2, max_row=row_max)

     titles = Reference(sheet, min_col=1, min_row=row_num+1, max_row=row_max)
     chart = BarChart()
     chart.title = "Statistics: Department Adverts"
     chart.add_data(data=data, titles_from_data=True)
     chart.set_categories(titles)
     chart.y_axis.title = 'Number of Adverts'
     chart.x_axis.title = 'Department Adverts'
     chart.height = 15
     chart.width = 30

     # Style the lines

     s2 = chart.series[0]

     #s2 = chart.series[1]
     s2.smooth = True # Make the line smooth

     sheet.add_chart(chart, f"G{row_num}")

     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])

     row_max = row_max + 13
     row_num = row_max

     regions = Region.objects.all()

     regions_graph = []
     regions_graph.append(('Regions','Number of Adverts'))
     for t in regions:
         if t.adverts.count() > 0:
             regions_graph.append((t.region, t.adverts.count()))

     for row in regions_graph:
         sheet.append(row)
         row_max = row_max + 1

     data = Reference(sheet, min_col=2, min_row=row_num, max_col=2, max_row=row_max)

     titles = Reference(sheet, min_col=1, min_row=row_num+1, max_row=row_max)
     chart = BarChart()
     chart.title = "Statistics: Region Adverts"
     chart.add_data(data=data, titles_from_data=True)
     chart.set_categories(titles)
     chart.y_axis.title = 'Number of Adverts'
     chart.x_axis.title = 'Region Adverts'
     chart.height = 7.5
     chart.width = 20

     # Style the lines

     s2 = chart.series[0]

     #s2 = chart.series[1]
     s2.smooth = True # Make the line smooth

     sheet.add_chart(chart, f"G{row_num}")


     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])
     sheet.append([''])

     row_max = row_max + 13
     row_num = row_max

     companies = Company.objects.all()

     companiess_graph = []
     companiess_graph.append(('Companies','Number of Adverts'))
     for t in companies:
         if t.adverts.count() > 0:
             companiess_graph.append((t.company_name, t.adverts.count()))

     for row in companiess_graph:
         sheet.append(row)
         row_max = row_max + 1

     data = Reference(sheet, min_col=2, min_row=row_num, max_col=2, max_row=row_max)

     titles = Reference(sheet, min_col=1, min_row=row_num+1, max_row=row_max)
     chart = BarChart()
     chart.title = "Statistics: Company Adverts"
     chart.add_data(data=data, titles_from_data=True)
     chart.set_categories(titles)
     chart.y_axis.title = 'Number of Adverts'
     chart.x_axis.title = 'Company Adverts'
     chart.height = 12.5
     chart.width = 30

     # Style the lines

     s2 = chart.series[0]

     #s2 = chart.series[1]
     s2.smooth = True # Make the line smooth

     sheet.add_chart(chart, f"G{row_num}")



     font_heading = Font(name='Calibri',size=12,bold=True,italic=False,vertAlign=None,underline='none',strike=False,color='FF000000')

     wb.save(response)

     return response


@login_required()
def print_advert_pdf(request,pk):

     buffer = BytesIO()
     c = Advert.objects.get(id=pk)
     company = MyPrintAdvert('A4')
     pdf_value = company.print_advert(pk)

     response = HttpResponse(content_type='application/pdf')
     response['Content-Disposition'] = f'attachment; filename="advert.pdf"'

     response.write(pdf_value)
     return response
