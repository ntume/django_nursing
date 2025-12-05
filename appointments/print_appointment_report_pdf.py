from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
import qrcode
import PyPDF2
import glob
import os
from datetime import timedelta
import uuid
from django.conf import settings
from appointments.models import Appointment
from pdfrw import PdfReader, PdfWriter, IndirectPdfDict
from students.models import Student



    
def add_watermark(wmFile, pageObj):
        # opening watermark pdf file
        wmFileObj = open(wmFile, 'rb')
        
        # creating pdf reader object of watermark pdf file
        pdfReader = PyPDF2.PdfFileReader(wmFileObj) 
        
        # merging watermark pdf's first page with passed page object.
        pageObj.mergePage(pdfReader.getPage(0))
        
        # closing the watermark pdf file object
        #wmFileObj.close()
        
        # returning watermarked page object
        return pageObj


class MyPrintAppointmentReport:

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = landscape(A4)
        elif pagesize == 'Letter':
            self.pagesize = landscape(letter)

        self.width, self.height = self.pagesize

    
    


    def print_report(self,filterstr):
        
        appts_uuid = uuid.uuid4()
        
        page_width, page_height = landscape(A4)
        margin = 50  # Margin in points (50pt = 0.7 inch approx.)
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin

        buffer = self.buffer
        doc = SimpleDocTemplate(f'media/reports/appts_{appts_uuid}.pdf',
                                rightMargin=40,
                                leftMargin=40,
                                topMargin=100,
                                bottomMargin=72,
                                pagesize=landscape(self.pagesize))

        # Our container for 'Flowable' objects
        elements = []

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        #styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        pageTextStyleCenter = ParagraphStyle(name="left", 
                                             alignment=TA_CENTER,
                                             spaceBefore = 20,
                                             fontSize= 20,
                                             spaceAfter = 20,)
            
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


        table_data = [[Paragraph('''<b>AHC NURSING COLLEGE (PTY) LTD</b><br/><br/>
                                    Appointments Report'''
                                ,pageTextStyleCenter)]]  
           
        profile_table = Table(table_data,colWidths=[usable_width])
        elements.append(profile_table)
        elements.append(Paragraph("<br/><br/>", styles['Heading3']))
               

        table_contents = [
                                [
                                    Paragraph('<b>Student</b>',styles['Normal']),
                                    Paragraph('<b>Student Number</b>',styles['Normal']),
                                    Paragraph('<b>Description</b>',styles['Normal']),
                                    Paragraph('<b>Date</b>',styles['Normal']),
                                    Paragraph('<b>Start Time</b>',styles['Normal']),
                                    Paragraph('<b>End Time</b>',styles['Normal']),
                                    Paragraph('<b>Category</b>',styles['Normal']),
                                    Paragraph('<b>Status</b>',styles['Normal']),
                                    Paragraph('<b>Outcome</b>',styles['Normal']),
                                ]
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
            
                
            table_contents.append(
                    [
                        Paragraph(f'{ student }',styles['Normal']),
                        Paragraph(f'{ student_number }',styles['Normal']),
                        Paragraph(f'{ appt.description }',styles['Normal']),
                        Paragraph(f'{ appt.appointment_date }',styles['Normal']),
                        Paragraph(f'{ appt.appointment_time_start }',styles['Normal']),
                        Paragraph(f'{ appt.appointment_time_end }',styles['Normal']),
                        Paragraph(f'{ category }',styles['Normal']),
                        Paragraph(f"{ appt.status }",styles['Normal']),
                        Paragraph(f"{ outcome }",styles['Normal']),
                    ]
                )

            
        modules_table = Table(
            table_contents,
            colWidths=[
                3.5 * cm, 2.0 * cm, 4.0 * cm, 2.5 * cm,
                2.5 * cm, 2.5 * cm, 2.5 * cm, 4.0 * cm, 3.0 * cm
            ]
        )
        modules_table.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ]))
        elements.append(modules_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))
            
        doc.build(elements,canvasmaker=NumberedCanvas)

        pdf_paths = [f'media/reports/appts_{appts_uuid}.pdf']
        
        writer = PdfWriter()
        for path in pdf_paths:
            reader = PdfReader(path)
            writer.addpages(reader.pages)

        writer.trailer.Info = IndirectPdfDict(
            Title='POP',
            Author='AHCNC',
            Subject='Appointments',
            Creator='AHC-NC'
        )

        writer.write(f'media/reports/appts_{appts_uuid}.pdf')
      
        pdf_file = f'media/reports/appts_{appts_uuid}.pdf'
        watermark = "media/letter_head_landscape.pdf"
        watermark_other_pages = "media/letter_head_landscape.pdf"
        merged_file = f"media/reports/appts_{appts_uuid}_merged.pdf"


        input_file = open(pdf_file,'rb')
        input_pdf = PyPDF2.PdfFileReader(input_file)

        watermark_file = open(watermark,'rb')
        watermark_pdf = PyPDF2.PdfFileReader(watermark_file)

        pdf_page = input_pdf.getPage(0)
        watermark_page = watermark_pdf.getPage(0)

        watermark_page.mergePage(pdf_page)
        output = PyPDF2.PdfFileWriter()
        output.addPage(watermark_page)

        for page in range(1, input_pdf.numPages):
            # creating watermarked page object
            wmpageObj = add_watermark(watermark_other_pages, input_pdf.getPage(page))          
            # adding watermarked page object to pdf writer
            output.addPage(wmpageObj)


        merged_file = open(merged_file,'wb')
        output.write(merged_file)
        merged_file.close()
        watermark_file.close()
        input_file.close()

        del_letter_tpl = f'reports/appts_{appts_uuid}.pdf'
        file_path = os.path.join(settings.MEDIA_ROOT, del_letter_tpl)

        if os.path.isfile(file_path):
            os.remove(file_path)

        return f"reports/appts_{appts_uuid}_merged.pdf"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(200 * mm, 15 * mm + (0.2 * mm),
                             "Page %d of %d" % (self._pageNumber, page_count))