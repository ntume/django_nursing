import datetime
from college.models import EducationPlanYear,EducationPlanYearSection,EducationPlanYearSectionWeeks
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


class MyPrintMasterPlan:

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter

        self.width, self.height = self.pagesize

    
    def print_masterplan(self,pk):
        plan = EducationPlanYear.objects.get(id = pk)

        page_width, page_height = landscape(A4)
        margin = 50  # Margin in points (50pt = 0.7 inch approx.)
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin

        
        global qrcode_image_file

        buffer = self.buffer
        doc = SimpleDocTemplate(f'media/generaldocuments/masterplan/{plan.id}.pdf',
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
                                    MASTER EDUCATIONAL PLAN {plan.year}<br/><br/>
                                    {plan.cohort_registration_period.learning_programme_cohort.learning_programme.programme_name}<br/>'''
                                ,pageTextStyleCenter)]]  
           
        profile_table = Table(table_data,colWidths=[usable_width])
        elements.append(profile_table)
        elements.append(Paragraph("<br/><br/>", styles['Heading3']))

        

        sections = plan.sections.all()
        
        for section in sections:

            recess_list = []
            recess_num = 1

            exam_list = []
            exam_num = 1

            lrt_list = []
            lrt_num = 1

            bl_list = []
            bl_num = 1

            sim_list = []
            sim_num = 1

            cpl_list = []
            cpl_num = 1
            
            sa_cpl_list = []
            sa_cpl_num = 1

            table_data = [[Paragraph(f'{section.section}',styles['Heading2'])]]  
           
            section_table = Table(table_data,colWidths=[usable_width])
            elements.append(section_table)
            elements.append(Paragraph("<br/>", styles['Heading3']))


            table_data = []
            week_row = [Paragraph('Week',styles['Normal'])]
            academic_row = [Paragraph('Academic Week',styles['Normal'])]
            date_row = [Paragraph('Date Week',styles['Normal'])]
            block_row = [Paragraph(f'{plan.cohort_registration_period.learning_programme_cohort.learning_programme.programme_name}',styles['Normal'])]
            
            for week in section.weeks.all():
                block,facility_type,time_period = '','',''
        
                if week.block:
                    block = week.block.block_code
                    if block == 'REC':
                        recess_list.append(recess_num)

                    if block == 'EX':
                        exam_list.append(exam_num)

                    if block == 'LRT':
                        lrt_list.append(lrt_num)

                    if block == 'BL' or block == 'REG + OR' or block == 'RV':
                        bl_list.append(bl_num)

                    if block == 'SIM':
                        sim_list.append(sim_num)

                    if block == 'CPL':
                        cpl_list.append(cpl_num)
                        
                    if block == 'SA CL/CPL' or block == 'SA CL/LRT':
                        sa_cpl_list.append(sa_cpl_num)

                if week.facility_type:
                    facility_type = week.facility_type

                if week.time_period:
                    time_period = week.time_period

                week_row.append(Paragraph(f'{week.week_number}',blockpageTextStyleCenter))
                academic_row.append(Paragraph(f'{week.academic_week_number}',blockpageTextStyleCenter))
                date_row.append(Paragraph(f'{week.start_of_week.strftime("%b %d")} - {week.end_of_week.strftime("%b %d")}',blockpageTextStyleCenter))
                block_row.append(Paragraph(f'{block} <br/> {facility_type} <br/> {time_period}',blockpageTextStyleCenter))

                recess_num = recess_num + 1
                exam_num = exam_num + 1
                lrt_num = lrt_num + 1
                bl_num = bl_num + 1
                sim_num = sim_num + 1
                cpl_num = cpl_num + 1
                sa_cpl_num = sa_cpl_num + 1

          
            first_column_width = usable_width * 0.1  # First column takes 40% of the width
            other_columns_width = (usable_width - first_column_width) / (len(week_row) - 1)  # Divide remaining width


            colWidths = [first_column_width] + [other_columns_width] * (len(week_row) - 1)
   
            table_data.append(week_row)    
            table_data.append(academic_row)      
            table_data.append(date_row)     
            table_data.append(block_row)  

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
            
            for recess in recess_list:
                tb_base_style.append(('BACKGROUND', (recess, 3), (recess, 3), colors.orange))

            for ex in exam_list:
                tb_base_style.append(('BACKGROUND', (ex, 3), (ex, 3), colors.red))

            for lrt in lrt_list:
                tb_base_style.append(('BACKGROUND', (lrt, 3), (lrt, 3), colors.lightgrey))

            for bl in bl_list:
                tb_base_style.append(('BACKGROUND', (bl, 3), (bl, 3), colors.lightgreen))

            for sim in sim_list:
                tb_base_style.append(('BACKGROUND', (sim, 3), (sim, 3), colors.cyan))

            for cpl in cpl_list:
                tb_base_style.append(('BACKGROUND', (cpl, 3), (cpl, 3), colors.cyan))
                
            for sa_cpl in sa_cpl_list:
                tb_base_style.append(('BACKGROUND', (sa_cpl, 3), (sa_cpl, 3), colors.pink))


            quarter_table.setStyle(TableStyle(tb_base_style))
            elements.append(quarter_table)
            elements.append(Paragraph("<br/>", styles['Heading3']))
            
        blocks = ProgarmmeBlock.objects.all()
        
        

        doc.build(elements)

        pdf_paths = [f'media/generaldocuments/masterplan/{plan.id}.pdf']
        
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

        writer.write(f'media/generaldocuments/masterplan/{plan.id}.pdf')
      

        filename = f'generaldocuments/masterplan/{plan.id}.pdf'

        file_path = os.path.join(settings.MEDIA_ROOT, filename)

            
        with open(file_path, "rb") as file_object:
            file_m3u8 = File(name='sor.pdf', file=file_object)
            plan.file.save('sor.pdf', file_m3u8)
            plan.save()

        return f"generaldocuments/masterplan/{plan.id}.pdf"

    

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
