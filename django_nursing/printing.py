from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from students.models import Student
from students.models import Student, StudentSubject, Country, StudentSubjectVisits, StudentSubjectPreviousCompany
from faculties.models import Subject

class MyPrint:

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = landscape(A4)
        elif pagesize == 'Letter':
            self.pagesize = landscape(letter)

        self.width, self.height = self.pagesize


    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header = Paragraph('<img src="static/images/logo.png" height="90" width="200"/>', styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        # Footer
        footer = Paragraph('This is a multi-line footer.  It goes on every page.   ' * 5, styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

    def print_students(self,subject_id):

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
        rightMargin=60,
        leftMargin=60,
        topMargin=100,
        bottomMargin=72,
        pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        students = StudentSubject.objects.filter(subject_id = subject_id)
        subject = Subject.objects.get(id = subject_id)
        subject = "List of Students - {} - {} S{}".format(subject.program.programme_code,subject.year,subject.semester)
        elements.append(Paragraph(subject, styles['Heading4']))

         # Need a place to store our table rows
        table_data = []
        table_data.append([Paragraph("Student Number", styles['Heading4']), Paragraph("Name", styles['Heading4']), Paragraph("Contacts", styles['Heading4']),Paragraph("Period", styles['Heading4']),Paragraph("Registration Date", styles['Heading4']),Paragraph("Company", styles['Heading4'])])
        for i, studsubj in enumerate(students):
            # Add a row to the table
            name = "{} {}".format(studsubj.student.name,studsubj.student.surname)


            table_data.append(
                              [studsubj.student.student_number,
                               name,
                               Paragraph("{}<br/>{}".format(studsubj.student.email,studsubj.student.contact_number),styles['Normal']),
                               studsubj.period.period,
                               studsubj.registration_date,
                               Paragraph("{}<br/>{}<br/>{}".format(studsubj.company.company_name,studsubj.mentor.fullname,studsubj.mentor.email),styles['Normal'])]
                              )
        # Create the table
        user_table = Table(table_data)
        user_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(user_table)

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages= self._header_footer,canvasmaker=NumberedCanvas)

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


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
        self.drawRightString(211 * mm, 15 * mm + (0.2 * mm),
                             "Page %d of %d" % (self._pageNumber, page_count))
