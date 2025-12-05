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

from students.models import StudentLearningProgramme


@login_required()
def print_cohort_vaccination_list_excel(request,pk):

    '''
    Print cohort vaccination list
    '''

    if request.user.logged_in_role_id == 2 or request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 6:

        students = StudentLearningProgramme.objects.filter(learning_programme_cohort_id = pk)

        rows = [
                    (
                        "Student Number",
                        "ID Number",
                        "Full Name",
                        "Email",
                        "Doses",                                           
                    )
        ]

        for student in students:

            dose_list = [
                vaccine for vaccine in student.vaccinations.values_list('vaccine__dose', flat=True) if vaccine
            ]
           
            doses = ', '.join(dose_list)

            row_tuple = (
                f"{ student.student.student_number }",
                f"{ student.student.id_number }",
                f"{ student.student.first_name } { student.student.last_name }",
                f"{ student.student.email }",            
                f"{ doses }",                                     
            )

            rows.append(row_tuple)

        
        # Call a Workbook() function of openpyxl
        # to create a new blank Workbook object
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="cohort_vaccination_list.xlsx"'

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