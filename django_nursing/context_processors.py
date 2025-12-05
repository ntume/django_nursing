from django.contrib import messages
from django.shortcuts import render,redirect
from college.models import HealthCareFacilityHOD, LearningProgramme
from funder.models import Funder
from students.models import Student
from todo.models import Task
from events.models import Event
import datetime


def menu_roles(request):
    if request.user.is_authenticated:
        roles = request.user.roles.all()
        return {'MENU_USER_ROLES':roles}

    return {'MENU_USER_ROLES':'None'}


def menu_fetch_student(request):
    if request.user.is_authenticated:
        if request.user.logged_in_role_id == 10:
            student = Student.objects.get(user = request.user)
        
            return {'MENU_STUDENT':student}

    return {'MENU_STUDENT':'None'}

def menu_designation(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 1:
            menu_designation = {'role':request.user.roles.role}
            return {'MENU_DESIGNATION':menu_designation}

        elif request.user.roles_id == 2:
            try:
                LecturerUser = Lecturer.objects.get(user_id=request.user.id)
                menu_designation = {'role':request.user.roles.role,'department':LecturerUser.department.department,'faculty':LecturerUser.department.faculty.faculty}
                return {'MENU_DESIGNATION':menu_designation}
            except:
                messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
                return redirect('accounts:logout')

        elif request.user.roles_id == 3:
            try:
                company_contact = CompanyContacts.objects.get(user_id=request.user.id)
                menu_designation = {'role':request.user.roles.role,'company_contact':company_contact}
                return {'MENU_DESIGNATION':menu_designation}
            except:
                messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
                return redirect('accounts:logout')

        elif request.user.roles_id == 4:
            try:
                site_appointments = SiteConfig.objects.get(config = 'appointments')
                studentUser = Student.objects.get(user_id=request.user.id)
                subjects = StudentSubject.objects.filter(student = studentUser,completed__exact='No')
                menu_designation = {'site_appointments':site_appointments,'role':request.user.roles.role,'department':studentUser.department.department,'faculty':studentUser.department.faculty.faculty,'student':studentUser,'subjects':subjects}
                return {'MENU_DESIGNATION':menu_designation}
            except:
                messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
                return redirect('accounts:logout')

        elif request.user.roles_id == 6:
            try:
                site_appointments = SiteConfig.objects.get(config = 'appointments')
                studentUser = Student.objects.get(user_id=request.user.id)
                menu_designation = {'site_appointments':site_appointments,'role':request.user.roles.role,'department':studentUser.department.department,'faculty':studentUser.department.faculty.faculty,'student':studentUser}
                return {'MENU_DESIGNATION':menu_designation}
            except:
                messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
                return redirect('accounts:logout')

        elif request.user.roles_id == 9:
            menu_designation = {'role':request.user.roles.role}
            return {'MENU_DESIGNATION':menu_designation}

        elif request.user.roles_id == 10:
            menu_designation = {'role':request.user.roles.role,'department':'','faculty':''}
            return {'MENU_DESIGNATION':menu_designation}

        elif request.user.roles_id == 11:
            menu_designation = {'role':request.user.roles.role,'department':'','faculty':''}
            return {'MENU_DESIGNATION':menu_designation}

        elif request.user.roles_id == 12:
            try:
                MentorUser = Mentor.objects.get(user_id=request.user.id)
                menu_designation = {'role':request.user.roles.role,'mentor':MentorUser}
                return {'MENU_DESIGNATION':menu_designation}
            except:
                messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
                return redirect('accounts:logout')

    return {'MENU_DESIGNATION':'None'}

def menu_subjects(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 2:
            LecturerUser = Lecturer.objects.get(user_id=request.user.id)
            menu_subjects = Subject.objects.filter(program__department = LecturerUser.department, active__exact = 'Yes').order_by('-year','-semester','program__programme_code').select_related('program')
            return {'MENU_SUBJECTS':menu_subjects}

    return {'MENU_SUBJECTS':'None'}

def menu_programmes(request):
    if request.user.is_authenticated:
        if (request.user.logged_in_role_id == 2 or 
            request.user.logged_in_role_id == 1 or 
            request.user.logged_in_role_id == 3 or             
            request.user.logged_in_role_id == 4 or 
            request.user.logged_in_role_id == 12 or 
            request.user.logged_in_role_id == 7 or
            request.user.logged_in_role_id == 6):            
            menu_programmes = LearningProgramme.objects.all()
            return {'MENU_PROGRAMMES':menu_programmes}

    return {'MENU_PROGRAMMES':'None'}


def menu_funders(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 2:
            menu_funders = Funder.objects.all()
            return {'MENU_FUNDERS':menu_funders}

    return {'MENU_FUNDERS':'None'}

def menu_regions(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 2 or request.user.roles_id == 1 or request.user.roles_id == 9:
            menu_regions = Region.objects.all()
            return {'MENU_REGIONS':menu_regions}

    return {'MENU_REGIONS':'None'}


def menu_faculties(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 1 or request.user.roles_id == 9  or request.user.roles_id == 11  or request.user.roles_id == 10:
            menu_faculties = Faculty.objects.all()
            return {'MENU_FACULTIES':menu_faculties}

    return {'MENU_FACULTIES':'None'}

def menu_company_departments(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 12:
            MentorUser = Mentor.objects.get(user_id = request.user.id)
            menu_company_departments = CompanyDepartment.objects.filter(company = MentorUser.company)
            return {'MENU_COMPANY_DEPARTMENTS':menu_company_departments}

        elif request.user.roles_id == 3:
            company_contact = CompanyContacts.objects.get(user_id = request.user.id)
            menu_company_departments = company_contact.departments.all()
            return {'MENU_COMPANY_DEPARTMENTS':menu_company_departments}

    return {'MENU_COMPANY_DEPARTMENTS':'None'}

def menu_fetch_tasks(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 2 or request.user.roles_id == 10:
            tasks = Task.objects.filter(user_id = request.user.id,status__exact='Pending')
            return {'MENU_TASKS':tasks}

    return {'MENU_TASKS':'None'}

def menu_fetch_appointments(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 2:
            LecturerUser = Lecturer.objects.get(user_id=request.user.id)
            appointments = StudentSubjectVisits.objects.filter(studentsubject__subject__program__department = LecturerUser.department,completed='No',lecturer=LecturerUser).order_by('-date_visit')
            return {'MENU_APPOINTMENTS':appointments}

    return {'MENU_APPOINTMENTS':'None'}

def menu_fetch_student_appointments(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 4 or request.user.roles_id == 6:
            student_user = Student.objects.get(user_id=request.user.id)
            appointments = Appointment.objects.filter(student = student_user).exclude(status='Completed').order_by('-appointment_date')
            return {'MENU_STUDENT_APPOINTMENTS':appointments}

        if request.user.roles_id == 10:
            appointments = Appointment.objects.filter(assigned = request.user).exclude(status='Completed').order_by('-appointment_date')
            return {'MENU_STUDENT_APPOINTMENTS':appointments}

    return {'MENU_STUDENT_APPOINTMENTS':'None'}


def menu_fetch_interviews(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 4 or request.user.roles_id == 6:
            student_user = Student.objects.get(user_id=request.user.id)
            interviews = student_user.interviews.filter(interview__completed__exact = 'No',interview__date_interview__gte=datetime.date.today()).order_by('-interview__date_interview')
            return {'MENU_INTERVIEWS':interviews}

        if request.user.roles_id == 10:
            interviews = Interview.objects.filter(date_interview__gte=datetime.date.today()).exclude(completed='Yes').order_by('-date_interview')
            return {'MENU_INTERVIEWS':interviews}

        if request.user.roles_id == 2:
            LecturerUser = Lecturer.objects.get(user_id=request.user.id)
            interviews = LecturerUser.department.interviews.filter(date_interview__gte=datetime.date.today()).exclude(completed='Yes').order_by('-date_interview')
            return {'MENU_INTERVIEWS':interviews}

    return {'MENU_INTERVIEW':'None'}


def menu_fetch_events(request):
    if request.user.is_authenticated:
        if request.user.roles_id == 2:
            LecturerUser = Lecturer.objects.get(user_id=request.user.id)
            events = LecturerUser.department.faculty.events.filter(event_date__gte=datetime.date.today()).order_by('event_date')
            return {'MENU_EVENTS':events}

        if request.user.roles_id == 10:
            events = Event.objects.filter(event_date__gte=datetime.date.today()).order_by('event_date')
            return {'MENU_EVENTS':events}

    return {'MENU_EVENTS':'None'}


def menu_fetch_wards(request):
    if request.user.is_authenticated:
        if request.user.logged_in_role_id == 11:
            hod = HealthCareFacilityHOD.objects.get(user_id=request.user.id)
            menu_wards = hod.wards.all()
            return {'MENU_WARDS':menu_wards,'healthcare_facility':hod.facility}

    return {'MENU_WARDS':'None','healthcare_facility':'None'}


def menu_current_date(request):
    if request.user.is_authenticated:
        today = datetime.date.today()
        return {'MENU_TODAY':today,}

    return {'MENU_TODAY':'None',}