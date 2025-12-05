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

from students.models import Student

from .models import *


@login_required()
def print_resource_list_excel(request,filterstr):

    '''
    Print resource booking List
    '''

    booking_list = ResourceBooking.objects.all().select_related('resource', 'user', 'role')

    
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

      
    row_count = 0

    rows = [
                (
                    "Name",
                    "Role",
                    "Resource",
                    "Quantity",
                    "Date",
                    "Start Time",
                    "End Time",
                    "Status",
                )
    ]

    for booking in booking_list:
       
        student = ''
        student_number = ''
        outcome = ''
        category = ''
        
        row_tuple = (
            f"{ booking.user.first_name } { booking.user.last_name }",
            f"{ booking.role.role }",
            f"{ booking.resource.resource }",
            f"{ booking.number_of_resources }",
            f"{ booking.booking_date }",
            f"{ booking.booking_time_start }",
            f"{ booking.booking_time_end }",
            f"{ booking.status }",      
        )

        rows.append(row_tuple)


    # Call a Workbook() function of openpyxl
    # to create a new blank Workbook object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="booking_report_list.xlsx"'

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