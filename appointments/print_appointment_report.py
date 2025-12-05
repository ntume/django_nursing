from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
import datetime
from io import BytesIO
import time
import uuid
import os
import random
import openpyxl
from openpyxl.chart import BubbleChart, Reference, Series, BarChart, LineChart
from openpyxl.styles import Font, Color

from .models import *


@login_required()
def print_appointment_list_excel(request,filterstr):

    '''
    Print Appointments List
    '''

    report_appointments_list = Appointment.objects.all()
    
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

      
    row_count = 0

    rows = [
                (
                    "Student",
                    "Student Number",
                    "Description",
                    "Date",
                    "Start Time",
                    "End Time",
                    "Category",
                    "Status",
                    "Outcome",
                )
    ]

    for appt in report_appointments_list:
       
        student = ''
        student_number = ''
        outcome = ''
        category = ''
        
        if appt.student:
            student = f'{ appt.student.first_name } { appt.student.last_name }'
            student_number = appt.student.student_number
            
        outcome = appt.get_outcome_summary()  
        
        if appt.category:
            category = appt.category.category         


        row_tuple = (
            f"{ student }",
            f"{ student_number }",
            f"{ appt.description }",
            f"{ appt.appointment_date }",
            f"{ appt.appointment_time_start }",
            f"{ appt.appointment_time_end }",
            f"{ category }",
            f"{ appt.status }",
            f"{ outcome }",            
        )

        rows.append(row_tuple)


    # Call a Workbook() function of openpyxl
    # to create a new blank Workbook object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="appointment_report_list.xlsx"'

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