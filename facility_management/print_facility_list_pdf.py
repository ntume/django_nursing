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
from facility_management.models import FacilityActivityBooking
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


class MyPrintFacilityReport:

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = landscape(A4)
        elif pagesize == 'Letter':
            self.pagesize = landscape(letter)

        self.width, self.height = self.pagesize

    
    


    def print_report(self,filterstr):
        
        facility_uuid = uuid.uuid4()
        
        page_width, page_height = landscape(A4)
        margin = 50  # Margin in points (50pt = 0.7 inch approx.)
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin

        buffer = self.buffer
        doc = SimpleDocTemplate(f'media/reports/facilities_{facility_uuid}.pdf',
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
            
        booking_list = FacilityActivityBooking.objects.all().select_related('facility_activity', 'user', 'role')

    
        if filterstr and filterstr != 'None':
            filter = filterstr.split('-')

            if filter[0] != "0":
                booking_list = booking_list.filter(facility_activity_id = filter[0])
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


        table_data = [[Paragraph('''<b>AHC NURSING COLLEGE (PTY) LTD</b><br/><br/>
                                    Facilities Management Report'''
                                ,pageTextStyleCenter)]]  
           
        profile_table = Table(table_data,colWidths=[usable_width])
        elements.append(profile_table)
        elements.append(Paragraph("<br/><br/>", styles['Heading3']))
               

        table_contents = [
                                [
                                    Paragraph('<b>Name</b>',styles['Normal']),
                                    Paragraph('<b>Role</b>',styles['Normal']),
                                    Paragraph('<b>Facility</b>',styles['Normal']),
                                    Paragraph('<b>Activity</b>',styles['Normal']),
                                    Paragraph('<b>Date</b>',styles['Normal']),
                                    Paragraph('<b>Start Time</b>',styles['Normal']),
                                    Paragraph('<b>End Time</b>',styles['Normal']),
                                    Paragraph('<b>Description</b>',styles['Normal']),
                                    Paragraph('<b>Status</b>',styles['Normal']),
                                ]
                            ]
        
        for booking in booking_list:
            
                
            table_contents.append(
                    [
                        Paragraph(f'{ booking.user.first_name } { booking.user.last_name }',styles['Normal']),
                        Paragraph(f'{ booking.role.role }',styles['Normal']),
                        Paragraph(f'{ booking.facility_activity.facility.facility }',styles['Normal']),
                        Paragraph(f'{ booking.facility_activity.activity.activity }',styles['Normal']),
                        Paragraph(f'{ booking.booking_date }',styles['Normal']),
                        Paragraph(f'{ booking.booking_time_start }',styles['Normal']),
                        Paragraph(f'{ booking.booking_time_end }',styles['Normal']),
                        Paragraph(f'{ booking.booking_description }',styles['Normal']),
                        Paragraph(f"{ booking.status }",styles['Normal']),
                    ]
                )

            
        modules_table = Table(
            table_contents,
            colWidths=[
                3.5 * cm, 2.5 * cm, 3.5 * cm, 3.0 * cm,
                2.0 * cm, 2.2 * cm, 2.5 * cm, 4.0 * cm, 2.1 * cm
            ]
        )
        modules_table.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ]))
        elements.append(modules_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))
            
        doc.build(elements,canvasmaker=NumberedCanvas)

        pdf_paths = [f'media/reports/facilities_{facility_uuid}.pdf']
        
        writer = PdfWriter()
        for path in pdf_paths:
            reader = PdfReader(path)
            writer.addpages(reader.pages)

        writer.trailer.Info = IndirectPdfDict(
            Title='POP',
            Author='AHCNC',
            Subject='Facilities Report',
            Creator='AHC-NC'
        )

        writer.write(f'media/reports/facilities_{facility_uuid}.pdf')
      
        pdf_file = f'media/reports/facilities_{facility_uuid}.pdf'
        watermark = "media/letter_head_landscape.pdf"
        watermark_other_pages = "media/letter_head_landscape.pdf"
        merged_file = f"media/reports/facilities_{facility_uuid}_merged.pdf"


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

        del_letter_tpl = f'reports/facilities_{facility_uuid}.pdf'
        file_path = os.path.join(settings.MEDIA_ROOT, del_letter_tpl)

        if os.path.isfile(file_path):
            os.remove(file_path)

        return f"reports/facilities_{facility_uuid}_merged.pdf"


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

