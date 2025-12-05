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
from pdfrw import PdfReader, PdfWriter, IndirectPdfDict



    
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


class MyPrintRegistrationForm:

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter

        self.width, self.height = self.pagesize

    

    def print_registration_form(self,student_registration):
        
          
        
        buffer = self.buffer
        doc = SimpleDocTemplate(f'media/college/registration_forms/{student_registration.id}.pdf',
        rightMargin=60,
        leftMargin=60,
        topMargin=100,
        bottomMargin=80,
        pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        #styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        pageTextStyleCenter = ParagraphStyle(name="left", alignment=TA_CENTER)
        
        addressStyle = ParagraphStyle(
            name="addressRightAligned",
            parent=styles["Normal"],
            fontSize=9,                   # smaller font
            alignment=TA_RIGHT,           # right align
            leading=10                    # adjust line spacing
        )
        
        smallStyle = ParagraphStyle(
            name="small",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
        )

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        
        table_data = [[Paragraph(f'PO Box 417<br/>Carletonville<br/>2500<br/>Tel:  +27 18 788 1248<br/>Fax:  +27 18 788 1247<br/>nursingcollege@africahealthcare.co.za',addressStyle),]]     
        title_table = Table(table_data,colWidths=[18.5 * cm])
        elements.append(title_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))
        
        table_data = [[Paragraph(f'<b>Registration Form</b><br/><br/>Date of Registration: {student_registration.registration_date}<br/>',smallStyle),]]     
        title_table = Table(table_data,colWidths=[18.5 * cm])
        elements.append(title_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))
        
        table_data = [[Paragraph(f'<b>Student Information</b>',pageTextStyleCenter),]]     
        title_table = Table(table_data,colWidths=[18.5 * cm])
        elements.append(title_table)
        
        race,gender,nationality = '','',''
        
        student = student_registration.student_learning_programme.student
        
        if student_registration.student_learning_programme.student.gender:
            gender = student_registration.student_learning_programme.student.gender.gender
            
        if student_registration.student_learning_programme.student.race:
            race = student_registration.student_learning_programme.student.race.race
            
        if student_registration.student_learning_programme.student.nationality:
            nationality = student_registration.student_learning_programme.student.nationality.nationality
        
        table_data = [
                      [Paragraph('Name/s',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.first_name}',smallStyle),],
                      [Paragraph('Surname',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.last_name}',smallStyle),],
                      [Paragraph('Maiden',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.maiden_name}',smallStyle),],
                      
                      [Paragraph('ID Number',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.id_number}',smallStyle),],
                      [Paragraph('Student Number',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.student_number}',smallStyle),],
                      [Paragraph('Postal Address',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.postal_address_1}, {student_registration.student_learning_programme.student.postal_address_2}, {student_registration.student_learning_programme.student.postal_address_3}',smallStyle),],
                      [Paragraph('Physical Address',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.physical_address_1}, {student_registration.student_learning_programme.student.physical_address_2}, {student_registration.student_learning_programme.student.physical_address_3}',smallStyle),],
                      
                      [Paragraph('E-mail Address',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.email}',smallStyle),],
                      [Paragraph('Cellphone',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.cellphone}',smallStyle),],
                      
                      [Paragraph('Gender',smallStyle),Paragraph(f'{gender}',smallStyle),],
                      [Paragraph('Race',smallStyle),Paragraph(f'{race}',smallStyle),],
                      [Paragraph('Date of Birth',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.dob}',smallStyle),],
                      
                      [Paragraph('Age',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.age}',smallStyle),],
                      [Paragraph('Disability',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.disability}',smallStyle),],
                      [Paragraph('Marital Status',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.marital_status}',smallStyle),],
                      [Paragraph('Nationality',smallStyle),Paragraph(f'{nationality}',smallStyle),],
                      [Paragraph('Indemnity Number',smallStyle),Paragraph(f'{student_registration.student_learning_programme.student.indemnity_number}',smallStyle),],
                       
                      ]
        main_table = Table(table_data,colWidths=[9.5 * cm, 9.0 * cm])
        main_table.setStyle(TableStyle([
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                    ]))
        elements.append(main_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))
        
        table_data = [[Paragraph(f'<b>Next of Kin</b>',pageTextStyleCenter),]]     
        title_table = Table(table_data,colWidths=[18.5 * cm])
        elements.append(title_table)
        
        table_contents = [
                                [
                                    Paragraph('<b>Name<br/>Code</b>',smallStyle),
                                    Paragraph('<b>ID Number</b>',smallStyle),
                                    Paragraph('<b>Contact Details</b>',smallStyle),
                                    Paragraph('<b>Email</b>',smallStyle),
                                    Paragraph('<b>Relationship</b>',smallStyle),
                                    Paragraph('<b>Employer</b>',smallStyle),
                                ]
                            ]
        
        for q in student.next_of_kin.all():
           
            
            table_contents.append(
                [
                    Paragraph(f'{ q.first_name } { q.last_name }',smallStyle),
                    Paragraph(f'{ q.id_number }',smallStyle),
                    Paragraph(f'{ q.cellphone}',smallStyle),
                    Paragraph(f'{ q.email}',smallStyle),
                    Paragraph(f'{ q.relationship }',smallStyle),
                    Paragraph(f'{ q.employer }',smallStyle),
                ]
            )

        
        modules_table = Table(table_contents,colWidths=[3 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm, 3.5 * cm,])
        modules_table.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ]))
        elements.append(modules_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))
        
        
        
        table_data = [[Paragraph(f'<b>Qualification/Programme Information</b>',pageTextStyleCenter),]]     
        title_table = Table(table_data,colWidths=[18.5 * cm])
        elements.append(title_table)
       

        learning_programme = student_registration.student_learning_programme.learning_programme

        table_data = [
                      [Paragraph('',smallStyle),Paragraph(f'<b>Qualification/Programme Information</b>',pageTextStyleCenter),],
                      [Paragraph('Qualification Name',smallStyle),Paragraph(f'{learning_programme.programme_name}',pageTextStyleCenter),],
                      [Paragraph('SAQA ID',smallStyle),Paragraph(f'{learning_programme.programme_code}',pageTextStyleCenter),],
                      [Paragraph('Qualification Code',smallStyle),Paragraph(f'{learning_programme.programme_code}',pageTextStyleCenter),],
                      [Paragraph('Study Period',smallStyle),Paragraph(f'{student_registration.registration_period.period.period}',pageTextStyleCenter),],
                      [Paragraph('Campus',smallStyle),Paragraph('CARLETONVILLE',pageTextStyleCenter),],
                      [Paragraph('Registration Period',smallStyle),Paragraph(f'{student_registration.registration_period.start_date} - {student_registration.registration_period.end_date}',pageTextStyleCenter),],
                      [Paragraph('Medium of Facilitation',smallStyle),Paragraph('Full-Time',pageTextStyleCenter),],
                      [Paragraph('Mode of Provisioning',smallStyle),Paragraph('Contact',pageTextStyleCenter),],
                      ]
        main_table = Table(table_data,colWidths=[9.5 * cm, 9.0 * cm])
        main_table.setStyle(TableStyle([
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                    ]))
        elements.append(main_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))


        table_data = [[Paragraph('<b>Registered Modules Information</b>',pageTextStyleCenter),]]     
        title_table = Table(table_data,colWidths=[18.5 * cm])
        elements.append(title_table)
        

        table_contents = [
                                [
                                    Paragraph('<b>Module<br/>Code</b>',smallStyle),
                                    Paragraph('<b>Module<br/>Description</b>',smallStyle),
                                    Paragraph('<b>Core/<br/>Fundamental</b>',smallStyle),
                                    Paragraph('<b>Duration</b>',smallStyle),
                                    Paragraph('<b>NQF<br/>Level</b>',smallStyle),
                                    Paragraph('<b>Credits</b>',smallStyle),
                                    Paragraph('<b>Exempt<br/>Y/N</b>',smallStyle),
                                    Paragraph('<b>Year<br/>Exam</b>',smallStyle),
                                    Paragraph('<b>Exam<br/>Month</b>',smallStyle),
                                    Paragraph('<b>Amount</b>',smallStyle),
                                ]
                            ]
        
        for q in student_registration.registered_modules.all():
            module = q.module.module
            
            if module:
                
                table_contents.append(
                    [
                        Paragraph(f'{ module.module_code }',smallStyle),
                        Paragraph(f'{ module.module_name }',smallStyle),
                        Paragraph(f'{ module.module_type }',smallStyle),
                        Paragraph('1 Year',smallStyle),
                        Paragraph(f'{ module.nqf_level.nqf_level }',smallStyle),
                        Paragraph(f'{ module.credits }',smallStyle),
                        Paragraph('N',smallStyle),
                        Paragraph('2025',smallStyle),
                        Paragraph('Nov',smallStyle),
                        Paragraph('R 4000',smallStyle),
                    ]
                )

            
        modules_table = Table(table_contents,colWidths=[2 * cm, 2.5 * cm, 2.5 * cm, 2.0 * cm, 1.5 * cm, 1.5 * cm, 2.0 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm])
        modules_table.setStyle(TableStyle([
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ]))
        elements.append(modules_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))
            
                
        doc.build(elements)

        pdf_paths = [f'media/college/registration_forms/{student_registration.id}.pdf']
        
        writer = PdfWriter()
        for path in pdf_paths:
            reader = PdfReader(path)
            writer.addpages(reader.pages)

        writer.trailer.Info = IndirectPdfDict(
            Title='POP',
            Author='AHCNC',
            Subject='Proof of Registration',
            Creator='AHC-NC'
        )

        writer.write(f'media/college/registration_forms/{student_registration.id}.pdf')
      
        pdf_file = f'media/college/registration_forms/{student_registration.id}.pdf'
        watermark = "media/letter_head.pdf"
        watermark_other_pages = "media/letter_head.pdf"
        merged_file = f"media/college/registration_forms/{student_registration.id}_merged.pdf"


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

        del_letter_tpl = f'college/registration_forms/{student_registration.id}.pdf'
        file_path = os.path.join(settings.MEDIA_ROOT, del_letter_tpl)

        if os.path.isfile(file_path):
            os.remove(file_path)

        return f"college/registration_forms/{student_registration.id}_merged.pdf"


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
