from tempfile import NamedTemporaryFile
from django.shortcuts import render,HttpResponse,redirect,Http404
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A6,A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib import messages
import boto3
from college.models import LearningProgrammeCohort
from django_nursing import settings
from .models import Student, StudentLearningProgramme  # Import Student model
import requests
from io import BytesIO
from django.core.files.base import ContentFile


def fetch_image_from_s3(image_key):
    """
    Download an image from AWS S3 and return its temporary file path.
    """
    # Initialize S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    # Define the bucket name
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    try:
        # Download the image as a byte stream
        image_obj = s3_client.get_object(Bucket=bucket_name, Key=image_key)
        image_data = image_obj["Body"].read()  # Read image bytes

        # Save to a temporary file
        temp_image = NamedTemporaryFile(delete=False, suffix=".png")  # Adjust suffix based on image format
        temp_image.write(image_data)
        temp_image.flush()

        return temp_image.name  # Return the temporary file path

    except Exception as e:
        print(f"Error downloading image from S3: {e}")
        return None  # Handle errors gracefully

def generate_student_card(request, pk):
    # Fetch student from database
    
    student_learning_programme = get_object_or_404(StudentLearningProgramme, id=pk)
    student = student_learning_programme.student
    
    # Create a BytesIO buffer to store the PDF
    pdf_buffer = BytesIO()

    # Create response object with PDF content type
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="student_card_{pk}.pdf"'

    # Set up ReportLab Document (A6 size in portrait mode)
    width, height = A4  # A6 size (105mm × 148mm)
    doc = SimpleDocTemplate(pdf_buffer, pagesize=(height, width))

    elements = []  # List to store table data
    styles = getSampleStyleSheet()  # Load default styles for text formatting

    # Student details
    student_name = f'{student.first_name} {student.last_name}'
    expiry_date = "2026/12/31"  # Format date
    college_name = "AHC Nursing College"
    college_address = "P.O. Box 417\nCarletonville\n2500"

    # PNG Logo URL (Replace with your actual PNG file URL)
    logo_url = "https://bms-nursing-media.s3.eu-west-1.amazonaws.com/static/images/AHC-LOGO.png"

    logo_image = None
    try:
        logo_path = fetch_image_from_s3('static/images/AHC-LOGO.png')
        try:           
            logo_image = ImageReader(logo_path)
            logo_img = Image(logo_path, width=60, height=40)
            
        except requests.exceptions.RequestException:
            logo_img = Paragraph("<b>[Logo Missing]</b>", styles["Normal"])
        except Exception as e:
            print(str(e))
            
    except requests.exceptions.RequestException:
        logo_img = Paragraph("<b>[Logo Missing]</b>", styles["Normal"])

    # Load student photo from Azure Blob Storage (Using URL)
    student_img = Paragraph("<b>[Photo Missing]</b>", styles["Normal"])
    if student.profile_pic:
        student_photo_path = fetch_image_from_s3(f'media/{student.profile_pic.name}')  # Get URL of the stored image
     
        try:  
            print(student_photo_path)          
            student_img = Image(student_photo_path, width=80, height=80)
            
        except requests.exceptions.RequestException:
            student_img = Paragraph("<b>[Photo Missing]</b>", styles["Normal"])
        except Exception as e:
            print(str(e))
    else:
        student_img = Paragraph("<b>[Photo Missing]</b>", styles["Normal"])

    # Create a row with student photo and logo **side by side**
    image_row = [student_img, logo_img]  # Images are in the same row
    image_table = Table(
        [[student_img, logo_img]],
        colWidths=[120, 60]
    )
    image_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # First column (left)
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Second column (right)
    ]))

    # Student Name & Number (Below the images in the same column)
    name_paragraph = Paragraph(f"<br/><br/><b>Name:</b> {student_name}<br/><br/><b>Student No:</b> {student.student_number}<br/><br/>", styles["Normal"])

    # Right column: Return details and expiry date
    return_paragraph = Paragraph(
        "<br/><b>If found, please return to:</b><br/>"
        f"{college_name}<br/>{college_address}<br/><br/><br/>"
        f"<b>Expiry Date:</b> {expiry_date}",
        styles["Normal"]
    )

    # Full left column (photo + logo + name + student no)
    left_column = [[image_table ], [name_paragraph]]

    # Full right column (return address + expiry date)
    right_column = [[return_paragraph]]

    # Create table with two columns
    table = Table([
        [left_column, right_column]  # Left & Right sections
    ], colWidths=[width * 0.35, width * 0.35])  # Two equal columns

    # Apply table styles
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align everything to the top
        ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Add border
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid inside table
        ('PADDING', (0, 0), (-1, -1), 5),  # Padding inside cells
        ('LEFTPADDING', (0, 0), (-1, -1), 20), # Apply 20 units of left padding to all cells
    ]))

    # Add table to elements list
    elements.append(table)

    # Build PDF
    doc.build(elements)
    
    # Save PDF to the Student model
    pdf_buffer.seek(0)
    student.student_card.save(f"student_card_{student.id_number}.pdf", ContentFile(pdf_buffer.read()), save=True)

    messages.success(request,'Successfully created student card')

    return redirect('students:cohort_learners',pk=student_learning_programme.learning_programme_cohort_id)




def generate_cohort_student_cards(request, pk):
    # Fetch student from database
    
    learning_programme_cohort = get_object_or_404(LearningProgrammeCohort, id=pk)
    students = learning_programme_cohort.students.all()
    
    # Create a BytesIO buffer to store the PDF
    pdf_buffer = BytesIO()

    # Create response object with PDF content type
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="student_card_{pk}.pdf"'

    # Set up ReportLab Document (A6 size in portrait mode)
    width, height = A4  # A6 size (105mm × 148mm)
    doc = SimpleDocTemplate(pdf_buffer, pagesize=(height, width))

    elements = []  # List to store table data
    styles = getSampleStyleSheet()  # Load default styles for text formatting

    
    expiry_date = "2026/12/31"  # Format date
    college_name = "AHC Nursing College"
    college_address = "P.O. Box 417\nCarletonville\n2500"

    # PNG Logo URL (Replace with your actual PNG file URL)
    logo_url = "https://sims-ahc-media.s3.eu-west-1.amazonaws.com/static/images/AHC-LOGO.png"

    logo_image = None
    try:
        logo_path = fetch_image_from_s3('static/images/AHC-LOGO.png')
        try:           
            logo_image = ImageReader(logo_path)
            logo_img = Image(logo_path, width=60, height=40)
            
        except requests.exceptions.RequestException:
            logo_img = Paragraph("<b>[Logo Missing]</b>", styles["Normal"])
        except Exception as e:
            print(str(e))
            
    except requests.exceptions.RequestException:
        logo_img = Paragraph("<b>[Logo Missing]</b>", styles["Normal"])
        
    
    for student_cohort in students:
        
        # Student details
        student_name = f'{student_cohort.student.first_name} {student_cohort.student.last_name}'

        # Load student photo from Azure Blob Storage (Using URL)
        student_img = Paragraph("<b>[Photo Missing]</b>", styles["Normal"])
        if student_cohort.student.profile_pic:
            student_photo_path = fetch_image_from_s3(f'media/{student_cohort.student.profile_pic.name}')  # Get URL of the stored image
        
            try:  
                print(student_photo_path)          
                student_img = Image(student_photo_path, width=80, height=80)
                
            except requests.exceptions.RequestException:
                student_img = Paragraph("<b>[Photo Missing]</b>", styles["Normal"])
            except Exception as e:
                print(str(e))
        else:
            student_img = Paragraph("<b>[Photo Missing]</b>", styles["Normal"])

        # Create a row with student photo and logo **side by side**
        image_row = [student_img, logo_img]  # Images are in the same row
        image_table = Table(
            [[student_img, logo_img]],
            colWidths=[120, 60]
        )
        image_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))

        # Student Name & Number (Below the images in the same column)
        name_paragraph = Paragraph(f"<br/><br/><b>Name:</b> {student_name}<br/><br/><b>Student No:</b> {student_cohort.student.student_number}", styles["Normal"])

        # Right column: Return details and expiry date
        return_paragraph = Paragraph(
            "<b>If found, please return to:</b><br/>"
            f"{college_name}<br/>{college_address}<br/><br/><br/>"
            f"<b>Expiry Date:</b> {expiry_date}",
            styles["Normal"]
        )

        # Full left column (photo + logo + name + student no)
        left_column = [[image_table ], [name_paragraph]]

        # Full right column (return address + expiry date)
        right_column = [[return_paragraph]]

        # Create table with two columns
        table = Table([
            [left_column, right_column]  # Left & Right sections
        ], colWidths=[width * 0.35, width * 0.35])  # Two equal columns

        # Apply table styles
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align everything to the top
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
            ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Add border
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid inside table
            ('PADDING', (0, 0), (-1, -1), 5),  # Padding inside cells
        ]))

        # Add table to elements list
        elements.append(table)

    # Build PDF
    doc.build(elements)
    
    # Save PDF to the Student model
    pdf_buffer.seek(0)
    learning_programme_cohort.student_cards.save(f"student_cards_{pk}.pdf", ContentFile(pdf_buffer.read()), save=True)

    messages.success(request,'Successfully created student card')

    return redirect('students:cohort_learners',pk=pk)