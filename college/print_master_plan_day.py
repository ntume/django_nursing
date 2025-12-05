import datetime
from college.models import EducationPlanYear,EducationPlanYearSection, EducationPlanYearSectionWeekDay,EducationPlanYearSectionWeeks
from reportlab.lib.pagesizes import letter, A4,A3, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus.flowables import KeepTogether
from django.core.files import File
import qrcode
import PyPDF2
import glob
import os
from datetime import datetime
import uuid
from django.conf import settings
from configurable.models import ProgarmmeBlock
from pdfrw import PdfReader, PdfWriter, IndirectPdfDict


    
def add_watermark(watermark, pdf_page):
        # opening watermark pdf file
        wmFileObj = open(watermark, 'rb')
        
        # creating pdf reader object of watermark pdf file
        wmpdfReader = PyPDF2.PdfFileReader(wmFileObj) 

        watermark_page = wmpdfReader.getPage(1)
        
        # merging watermark pdf's first page with passed page object.
        watermark_page.mergePage(pdf_page)
        
        # closing the watermark pdf file object
        #wmFileObj.close()
        
        # returning watermarked page object
        return watermark_page


class MyPrintMasterPlanWeek:

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter

        self.width, self.height = self.pagesize

    
    def print_masterplan_days(self,week_pk):
        days = EducationPlanYearSectionWeekDay.objects.filter(education_plan_section_week_id = week_pk)
        week = EducationPlanYearSectionWeeks.objects.get(id = week_pk)
        
        page_width, page_height = landscape(A4)
        margin = 50  # Margin in points (50pt = 0.7 inch approx.)
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin

        
        global qrcode_image_file

        buffer = self.buffer
        doc = SimpleDocTemplate(f'media/generaldocuments/masterplan/weeks/{week_pk}.pdf',
                                rightMargin=40,
                                leftMargin=40,
                                topMargin=95,
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
        
        blockpageTextStyleCenter = ParagraphStyle(name="left", 
                                             alignment=TA_CENTER,)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        
        

        table_data = [[Paragraph(f'''<b>AHC NURSING COLLEGE (PTY) LTD</b><br/><br/>
                                    MASTER EDUCATIONAL PLAN {week.education_plan_year_section.education_plan_year.year}<br/><br/>
                                    Week: {week.start_of_week} to {week.end_of_week}<br/><br/>
                                    {week.education_plan_year_section.education_plan_year.cohort_registration_period.learning_programme_cohort.learning_programme.programme_name}<br/>'''
                                ,pageTextStyleCenter)]]  
           
        profile_table = Table(table_data,colWidths=[usable_width])
        elements.append(profile_table)
        elements.append(Paragraph("<br/><br/>", styles['Heading3']))

        
        
        for day in days:
            
            if day.timetable_sessions.count() > 0:
                
                table_data = []

                table_data_header = [[Paragraph(f'{day.day}',styles['Heading2'])]]  
            
                section_table = Table(table_data_header,colWidths=[usable_width])
                elements.append(section_table)
                elements.append(Paragraph("<br/>", styles['Heading3']))
                
                
                week_row = []

                if week.block.block_name == 'Theory Block':
                    week_row = [Paragraph('Session',styles['Heading2']),
                                Paragraph('Duration',styles['Heading2']),
                                Paragraph('Module',styles['Heading2']),
                                Paragraph('Study Unit',styles['Heading2']),
                                Paragraph('Lecturers',styles['Heading2']),]
                elif week.block.block_name == 'Simulation':
                    week_row = [Paragraph('Session',styles['Heading2']),
                                Paragraph('Duration',styles['Heading2']),
                                Paragraph('Type',styles['Heading2']),
                                Paragraph('Procedures',styles['Heading2']),
                                Paragraph('Lecturers',styles['Heading2']),]
                    
                table_data.append(week_row)
                
                for session in day.timetable_sessions.all():
                    
                    if week.block.block_name == 'Theory Block':
                        row = [Paragraph(f'{session.session.title}',blockpageTextStyleCenter),
                                        Paragraph(f'{session.session.start_time} - {session.session.end_time}',blockpageTextStyleCenter),
                                        Paragraph(f'{session.module.module.module_code }',blockpageTextStyleCenter),
                                        Paragraph(f'{session.study_unit.study_unit_name}',blockpageTextStyleCenter),
                                        Paragraph(f'{session.lecture_list()}',blockpageTextStyleCenter),]
                        table_data.append(row)
                        
                    elif week.block.block_name == 'Simulation':
                        row = [Paragraph(f'{session.session.title}',blockpageTextStyleCenter),
                                        Paragraph(f'{session.session.start_time} - {session.session.end_time}',blockpageTextStyleCenter),
                                        Paragraph(f'{session.type_procedure }',blockpageTextStyleCenter),
                                        Paragraph(f'{session.procedure_list()}',blockpageTextStyleCenter),
                                        Paragraph(f'{session.lecture_list()}',blockpageTextStyleCenter),]
                        table_data.append(row)
                                     
                first_column_width = usable_width * 0.1  # First column takes 40% of the width
                other_columns_width = (usable_width - first_column_width) / (len(week_row) - 1)  # Divide remaining width

                colWidths = [first_column_width] + [other_columns_width] * (len(week_row) - 1)

                quarter_table = Table(table_data,colWidths)
                tb_base_style = [
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header row background
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
                            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Center align columns 2 to last
                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Left align the first column
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                            ('FONTSIZE', (0, 0), (-1, -1), 12),  # Font size
                        ]
                
                
                quarter_table.setStyle(TableStyle(tb_base_style))
                elements.append(quarter_table)
                elements.append(Paragraph("<br/>", styles['Heading3']))
            
        
        doc.build(elements)

        pdf_paths = [f'media/generaldocuments/masterplan/weeks/{week_pk}.pdf']
        
        writer = PdfWriter()
        for path in pdf_paths:
            reader = PdfReader(path)
            writer.addpages(reader.pages)

        writer.trailer.Info = IndirectPdfDict(
            Title='Masterplan',
            Author='AHC',
            Subject='Masterplan',
            Creator='AHC'
        )

        writer.write(f'media/generaldocuments/masterplan/weeks/{week_pk}.pdf')
      

        filename = f'generaldocuments/masterplan/weeks/{week_pk}.pdf'

        file_path = os.path.join(settings.MEDIA_ROOT, filename)

            
        with open(file_path, "rb") as file_object:
            file_m3u8 = File(name='sor.pdf', file=file_object)
            week.file.save('sor.pdf', file_m3u8)
            week.save()

        return f"generaldocuments/masterplan/weeks/{week_pk}.pdf"

    

class NumberedCanvas(canvas.Canvas):
    def __init__(self, id_num,*args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.id_num = id_num

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
        #self.drawRightString(200 * mm, 15 * mm + (0.2 * mm),"Page %d of %d" % (self._pageNumber, page_count))
        qrcode_image_file = f'media/etqa/assessor_moderator/letters/{self.id_num}.jpeg'
        self.drawImage(qrcode_image_file, 200 * mm, 15 * mm + (0.2 * mm), width=120, preserveAspectRatio=True, mask='auto')
