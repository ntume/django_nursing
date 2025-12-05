from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
from django.shortcuts import render,HttpResponse,redirect,Http404
from datetime import date
from io import BytesIO
import time
import uuid
import os
import random
import openpyxl
from openpyxl.chart import BubbleChart, Reference, Series, BarChart, LineChart
from openpyxl.styles import Font, Color

from college.models import EducationPlanYearSection, LearningProgrammeCohort, LearningProgrammeCohortRegistrationPeriod
from configurable.models import Discipline, Ward
from students.models import StudentEducationPlanSectionWILRequirement

today = date.today()
@login_required()
def print_learner_wil_hours_list_excel(request,pk,period_pk):

    '''
    Print wil hours Learner List
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        learning_programme_cohort = LearningProgrammeCohort.objects.get(id = pk)
        learning_programme = learning_programme_cohort.learning_programme
        learning_programme_cohort_period = LearningProgrammeCohortRegistrationPeriod.objects.get(id = period_pk)
        registrations = learning_programme_cohort_period.registrations.all()
        disciplines = Discipline.objects.all()
        wards = Ward.objects.all()

        students = []

        for registration in registrations:

            student_map = {'registration':registration}

            wil_hours = StudentEducationPlanSectionWILRequirement.objects.filter(student_education_plan_section__registration = registration)
            
            logsheets = registration.logsheets.all()
            

            plan_year_section = None

            #find out what section we are in
            plan_year_section_check = EducationPlanYearSection.objects.filter(start_date__lte = today, 
                                                                        end_date__gte = today,
                                                                        education_plan_year__cohort_registration_period = registration.registration_period)
            if plan_year_section_check.exists():
                plan_year_section = plan_year_section_check.first()

            discipline_hours = []
            ward_hours = []

            #check the discipline hours captured and summarize the information
            for d in disciplines:
                discipline_map = {'discipline':d}        
                #check if there are any hours captured
                discipline_map['hours'] = logsheets.filter(discipline = d).aggregate(Sum('hours'))['hours__sum'] or 0
                discipline_map['total_quarter_hours'] = logsheets.filter(discipline = d,
                                                                        date__gte = plan_year_section.start_date,
                                                                        date__lte=plan_year_section.end_date).aggregate(Sum('hours'))['hours__sum'] or 0
                #check required hours
                discipline_map['total_required_hours'] = wil_hours.filter(period_wil_requirement__discipline = d).aggregate(Sum('hours'))['hours__sum'] or 0
                discipline_map['total_required_quarter_hours'] = wil_hours.filter(period_wil_requirement__discipline = d,student_education_plan_section__education_plan_year_section = plan_year_section).aggregate(Sum('hours'))['hours__sum'] or 0
                discipline_hours.append(discipline_map)

            for w in wards:
                ward_map = {'ward':w}
                #check if there are any hours captured
                ward_map['hours'] = logsheets.filter(ward = w).aggregate(Sum('hours'))['hours__sum'] or 0
                ward_hours.append(ward_map)

            student_map['ward_hours'] = ward_hours

            student_map['discipline_hours'] = discipline_hours

            students.append(student_map)
        
        rows = []

        row_tuple_inital = ("","",)
        

        for d in disciplines:
            row_tuple_discipline = (
                f"{d.discipline}",
                "",
                "",
                "",
            )

            row_tuple_inital = row_tuple_inital + row_tuple_discipline

        rows.append(row_tuple_inital)

        row_tuple_row_two = (
                "Student Number",
                "Full Name",
        )

        for d in disciplines:
            row_tuple_discipline = (
                "Total Hours",
                "Total Required Hours",
                "Quarterly Hours",
                "Total Required Quarterly Hours",
            )

            row_tuple_row_two = row_tuple_row_two + row_tuple_discipline
        
        rows.append(row_tuple_row_two)

        for l in students:
            fullname,student_number ='',''   
            registration = l['registration']
            if registration.student_learning_programme.student.student_number:
                student_number = registration.student_learning_programme.student.student_number

            fullname = f"{registration.student_learning_programme.student.first_name} {registration.student_learning_programme.student.last_name}"

            row_tuple_student = (
                f"{ student_number }",
                f"{ fullname }",                
            )

            for d in l['discipline_hours']:
                rows_tuple_hours = (
                    d["hours"],
                    d["total_required_hours"],
                    d["total_quarter_hours"],
                    d["total_required_quarter_hours"],
                )

                row_tuple_student = row_tuple_student + rows_tuple_hours

            rows.append(row_tuple_student)


        # Call a Workbook() function of openpyxl
        # to create a new blank Workbook object
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="learner_wil_hours_list.xlsx"'

        wb = openpyxl.Workbook()

        # Get workbook active sheet
        # from the active attribute.
        sheet = wb.active

        row_count = 0

        for row in rows:
            sheet.append(row)
            row_count = row_count + 1

        wb.save(response)
        return response
    
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
