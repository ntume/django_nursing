from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch, cm
from reportlab.lib import colors
import glob
import os
from io import BytesIO
from django.conf import settings
from pdfrw import PdfReader, PdfWriter, IndirectPdfDict
from .models import Advert

PAGESIZE = (140 * mm, 216 * mm)
BASE_MARGIN = 5 * mm

class PdfCreatorAdvert:
    def add_page_number(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        page_number_text = "%d" % (doc.page)
        canvas.drawCentredString(
            0.75 * inch,
            0.75 * inch,
            page_number_text
        )
        canvas.restoreState()
    def get_body_style(self):
        sample_style_sheet = getSampleStyleSheet()
        body_style = sample_style_sheet['BodyText']
        body_style.fontSize = 18
        return body_style
    def build_pdf(self):
        pdf_buffer = BytesIO()
        my_doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=PAGESIZE,
            topMargin=BASE_MARGIN,
            leftMargin=BASE_MARGIN,
            rightMargin=BASE_MARGIN,
            bottomMargin=BASE_MARGIN
        )
        body_style = self.get_body_style()
        flowables = [
            Paragraph("First paragraph", body_style),
            Paragraph("Second paragraph", body_style)
        ]
        my_doc.build(
            flowables,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )
        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()
        return pdf_value

class MyPrintAdvert:

    def __init__(self, pagesize):

        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter

        self.width, self.height = self.pagesize


    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header = Paragraph('<img src="static/images/logo.png" height="70" width="70"/>', styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)


        # Release the canvas
        canvas.restoreState()

    def print_advert(self,pk):
        advert = Advert.objects.get(id = pk)

        departments = []
        for d in advert.departments.all():
            departments.append(d.department)

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            rightMargin=60,
            leftMargin=60,
            topMargin=100,
            bottomMargin=72,
            pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        #styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

        # Draw things on the PDF. Here's  where the PDF generation happens.



        title = "Advert Details"
        table_data = [
                      [Paragraph(title, styles['Heading3'])],
        ]
        title_table = Table(table_data,colWidths=[18.5 * cm])
        elements.append(title_table)

         # Need a place to store our table rows
        table_data = []
        table_data.append([Paragraph('Company Name',styles['Heading4']),Paragraph(' {}'.format(advert.company.company_name),styles['Normal'])])

        table_data.append([Paragraph('Position',styles['Heading4']),Paragraph(' {}'.format(advert.position),styles['Normal'])])

        table_data.append([Paragraph('Description',styles['Heading4']),Paragraph(' {}'.format(advert.description),styles['Normal'])])

        table_data.append([Paragraph('Type',styles['Heading4']),Paragraph(' {}'.format(advert.type.type),styles['Normal'])])

        table_data.append([Paragraph('Requirements',styles['Heading4']),Paragraph(' {}'.format(advert.requirements),styles['Normal'])])

        table_data.append([Paragraph('Address',styles['Heading4']),Paragraph(' {}'.format(advert.address),styles['Normal'])])

        table_data.append([Paragraph("Type of Contract",styles['Heading4']),Paragraph(' {}'.format(advert.contract),styles['Normal'])])

        table_data.append([Paragraph('Cut off date',styles['Heading4']),Paragraph(' {}'.format(advert.cut_off_date),styles['Normal'])])

        table_data.append([Paragraph('Departments',styles['Heading4']),Paragraph(f' {", ".join([str(department) for department in departments]) }',styles['Normal'])])


        # Create the table
        advert_table = Table(table_data,colWidths=[4 * cm, 14.5 * cm])
        elements.append(advert_table)
        elements.append(Paragraph("<br/>", styles['Heading3']))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages= self._header_footer,canvasmaker=NumberedCanvas)

        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()
        return pdf_value


    def concatenate(paths, output):
        writer = PdfWriter()
        for path in paths:
            reader = PdfReader(path)
            writer.addpages(reader.pages)
        writer.trailer.Info = IndirectPdfDict(
            Title='Combined PDF Title',
            Author='Michael Driscoll',
            Subject='PDF Combinations',
            Creator='The Concatenator'
        )
        writer.write(output)


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
