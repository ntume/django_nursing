from django.shortcuts import render, redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
import datetime
import xlwt

from .models import WorkshopRSVP,WorkshopType,Workshop
from .forms import WorkshopCreateForm, WorkshopDocumentForm, WorkshopTypeForm
from faculties.models import Faculty, Campus
from students.models import Student
from communications.models import Notification
from virtual_spaces.models import VirtualSpaceStudentDelegate, Type as VirtualSpaceType
from virtual_spaces.forms import VirtualSpaceForm

# Create your views here.

class WorkshopList(LoginRequiredMixin,ListView):
    template_name = 'workshops/list_all.html'
    model = Workshop
    context_object_name = 'workshops'

    def get_queryset(self):
        return Workshop.objects.all().order_by('workshop_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = WorkshopDocumentForm()
        context['form'] = form
        context['faculties'] = Faculty.objects.all()
        context['workshop_menu'] = 'active'
        context['space_types'] = VirtualSpaceType.objects.all()
        return context

class WorkshopStudentList(LoginRequiredMixin,ListView):
    template_name = 'workshops/list_students.html'
    model = Workshop
    context_object_name = 'workshops'

    def get_queryset(self):
        StudentUser = get_object_or_404(Student,user_id = self.request.user.id)
        workshops = StudentUser.department.faculty.workshops.filter(workshop_enddate__gte=datetime.date.today())
        print(workshops)
        return workshops

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = WorkshopDocumentForm()
        context['form'] = form
        context['workshop_menu'] = 'active'
        return context

class WorkshopRSVPList(LoginRequiredMixin,ListView):

    template_name = 'workshops/rsvp.html'
    context_object_name = 'rsvps'

    def get_queryset(self):
        StudentUser = get_object_or_404(Student,user_id = self.request.user.id)
        rsvps = StudentUser.rsvp_workshops.all()    
        return rsvps

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workshop_menu'] = 'active'
        return context

class WorkshopCreateView(LoginRequiredMixin,CreateView):
    template_name = 'workshops/create.html'
    form_class = WorkshopCreateForm
    success_message = "%(title)s was created successfully."
    error_message = "Unfortunately something went wrong, please try again"

    def form_valid(self, form):      
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        notification = Notification.objects.create(notification = 'New Workshop', title = self.object.title, type_id = self.object.id, type = 'WORKSHOP')
        notification.save()

        facs = self.request.POST.getlist('faculties[]')

        for fac in facs:
            faculty = Faculty.objects.get(id=fac)
            self.object.faculties.add(faculty)

        self.object.save()

        return redirect('psycad:workshop_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculties = Faculty.objects.all().order_by('faculty')
        context['faculties'] = faculties
        context['campuses'] = Campus.objects.all()
        context['workshop_menu'] = 'active'
        return context

@login_required()
def view_workshops_as(request):

    workshops = Workshop.objects.filter(workshop_enddate__gte=datetime.date.today())
    return render(request,'workshops/as_student.html',{'view_as':'student','workshops':workshops})


@login_required()
def add_workshop(request):
    print('in')
    if request.method == 'POST':
        form = WorkshopCreateForm(request.POST)
        if form.is_valid():
            workshop = form.save(commit=False)
            workshop.user = request.user
            workshop.save()

            facs = request.POST.getlist('faculties[]')

            for fac in facs:
                faculty = Faculty.objects.get(id=fac)
                workshop.faculties.add(faculty)

            workshop.campus_id = request.POST['campus']
            workshop.save()

            messages.success(request,"Successfully added workshop")

        else:
            messages.warning(request,form.errors)

    return redirect('psycad:workshop_list')


@login_required()
def edit_workshop(request,pk):
    if request.method == 'POST':
        workshop_instance = Workshop.objects.get(id=pk)
        form = WorkshopCreateForm(request.POST,instance=workshop_instance)

        if form.is_valid():
            workshop = form.save(commit=False)
            workshop.user = request.user
            workshop.save()
            messages.success(request,"Successfully edited workshop")
            return redirect('psycad:workshop_list')

        else:
            messages.warning(request,form.errors)
            types = WorkshopType.objects.all()
            form = WorkshopCreateForm(instance=workshop_instance)
            workshop_menu = 'active'
            return render(request,'workshops/edit.html',{'workshop':workshop,'types':types,'form':form,'workshop_menu':workshop_menu})

    elif request.method == 'GET':
        workshop = Workshop.objects.get(id=pk)
        types = WorkshopType.objects.all()
        campuses = Campus.objects.all()
        form = WorkshopCreateForm(instance=workshop)
        workshop_menu = 'active'
        return render(request,'workshops/edit.html',{'workshop':workshop,'types':types,'form':form,'workshop_menu':workshop_menu,'campuses':campuses})


class WorkshopUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'workshops/edit.html'
    model = Workshop
    context_object_name = 'workshop'
    pk_url_kwarg = 'pk'
    fields = ('title','description','registration','type','workshop_date','workshop_enddate','workshop_time','location','extra_information','published')

    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.user = self.request.user
        self.object.save()
        messages.success(self.request,'Successfully edited Workshop')
        return redirect('psycad:workshop_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = WorkshopType.objects.all()
        context['workshop_menu'] = 'active'
        return context


@login_required()
def add_workshop_file(request,pk):
    workshop_instance = Workshop.objects.get(id = pk)
    form = WorkshopDocumentForm(request.POST, request.FILES, instance = workshop_instance)
    if form.is_valid():
        form.save()
        messages.success(request,'Successfully uploaded file')
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:workshop_list')


@login_required()
def add_rsvp(request,pk):
    student_instance = Student.objects.get(user_id = request.user.id)
    workshop_instance = Workshop.objects.get(id = pk)
    chckrsvpexists = WorkshopRSVP.objects.filter(student=student_instance,workshop=workshop_instance)
    if chckrsvpexists.exists():
        messages.warning(request,"You have already RSVP'd to this workshop")
    else:
        rsvp = WorkshopRSVP.objects.create(workshop=workshop_instance, student = student_instance)
        rsvp.save()
        if workshop_instance.virtual_spaces.count() > 0:
            space = workshop_instance.virtual_spaces.first()
            check_student_exists = VirtualSpaceStudentDelegate.objects.filter(student = student_instance,virtual_space = space)
            if check_student_exists.exists():
                pass
            else:
                s = VirtualSpaceStudentDelegate(virtual_space = space,student = student_instance,user=request.user)
                s.save()       
        messages.success(request, 'Successfully added RSVP')

    return redirect('student:workshoplist')

@login_required()
def workshop_remove_rsvp(request,pk):
    chckrsvpexists = WorkshopRSVP.objects.get(id = pk)
    if chckrsvpexists:
        workshop_instance = Workshop.objects.get(id = chckrsvpexists.workshop.id)
        student_instance = chckrsvpexists.student
        chckrsvpexists.delete()
        if workshop_instance.virtual_spaces.count() > 0:
            space = workshop_instance.virtual_spaces.first()
            check_student_exists = VirtualSpaceStudentDelegate.objects.filter(student = student_instance,virtual_space = space)
            if check_student_exists.exists():
                stud = check_student_exists.first()
                stud.delete() 
        messages.success(request,"Successfully removed RSVP")
    else:
        messages.warning(request, 'An error ocurred, please try again')

    return redirect('student:workshoprsvp')

@login_required()
def workshop_delete(request,pk):
    try:
        workshop = Workshop.objects.get(id=pk)
        workshop.delete()
        messages.success(request,"Successfully deleted Workshop")
    except:
        messages.warning(request,"An error has occured, Workshop not deleted, please try again or contact your administrator")

    return redirect('psycad:workshop_list')


@login_required()
def workshop_publish(request,pk):
    try:
        workshop = Workshop.objects.get(id=pk)
        if workshop.published == 'Yes':
            workshop.published = 'No'
            workshop.save(update_fields=["published"])
            messages.success(request,"Successfully unpublished workshop")
        else:
            workshop.published = 'Yes'
            workshop.save(update_fields=["published"])
            messages.success(request,"Successfully Published workshop")

    except:
        messages.warning(request,"An error has occured, please try again or contact your administrator")

    return redirect('psycad:workshop_list')


@login_required()
def workshop_add_faculty(request,pk):
    try:
        workshop = Workshop.objects.get(id=pk)
        faculty = Faculty.objects.get(id=request.POST['faculty'])
        workshop.faculties.add(faculty)
        messages.success(request,"Successfully added faculty to workshop")
    except:
        messages.warning(request,"Something wrong happened, faculty was not added, please try again")

    return redirect('psycad:workshop_list')


@login_required()
def workshop_remove_faculty(request,pk,faculty_id):
    try:
        workshop = Workshop.objects.get(id=pk)
        faculty = Faculty.objects.get(id=faculty_id)
        workshop.faculties.remove(faculty)
        messages.success(request,"Successfully removed faculty from workshop")
    except:
        messages.warning(request,"Something wrong happened, faculty was not removed, please try again")

    return redirect('psycad:workshop_list')



class WorkshopTypeList(LoginRequiredMixin,ListView):

    template = 'workshops/workshoptype_list.html'
    model = WorkshopType
    context_object_name = 'types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = WorkshopTypeForm()
        context['form'] = form
        context['config_menu'] = 'active'
        return context


@login_required()
def add_workshoptypes(request):
    if request.user.roles_id == 10 or request.user.roles_id == 11:
        if request.method == 'POST':
            form = WorkshopTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,'Workshop type added successfully')
            else:
                messages.warning(request,form.errors)

        return redirect('psycad:config_workshoptypes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def edit_workshoptypes(request,pk):
    if request.user.roles_id == 10 or request.user.roles_id == 11:
        if request.method == "POST":
            try:
                type_instance = WorkshopType.objects.get(id = pk)
                if request.POST["task"] == "edit":
                    form = WorkshopTypeForm(request.POST,instance = type_instance)
                    if form.is_valid():
                        form.save()
                        messages.success(request,'Workshop type edited successfully')
                    else:
                        messages.warning(request,form.errors)

                if request.POST["task"] == "delete":
                    type_instance.delete()
                    messages.success(request,'Workshop type deleted successfully')

            except Exception as e:
                messages.warning(request,e.msg)

        return redirect('psycad:config_workshoptypes')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def workshop_add_virtual_space(request,pk):

    workshop = Workshop.objects.get(id = pk)
    form = VirtualSpaceForm(request.POST)
    if form.is_valid():
        space = form.save(commit = False)
        space.workshop = workshop
        space.user = request.user
        space.save()
        
        for student in workshop.rsvp_students.all():
            s = VirtualSpaceStudentDelegate(virtual_space = space,student = student.student,user=request.user)
            s.save()

        messages.success(request,'Successfully created a virtual space. Click on the virtual space to add rooms and view particpants')
    else:
        messages.warning(request,form.errors)

    return redirect('psycad:workshop_list')


@login_required()
def view_workshop_rsvps(request,pk):
    workshop = Workshop.objects.get(id = pk)
    rsvps = WorkshopRSVP.objects.filter(workshop = workshop)

    return render(request,'workshops/list_rsvps.html',{'workshop':workshop,'rsvps':rsvps})


@login_required()
def print_workshop_rsvps_excel(request,pk):

    workshop = Workshop.objects.get(id = pk)
    rsvps = WorkshopRSVP.objects.filter(workshop = workshop)

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

