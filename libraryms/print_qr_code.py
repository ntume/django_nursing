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
from .models import Book,BookCopy
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import ImageDraw, ImageFont
from PIL import Image as PilImage
import os
from django.contrib.auth.decorators import login_required
from django.core.files import File
import qrcode

@login_required()
def book_copy_print_qr_code(request, pk, copy_pk):
    if request.user.logged_in_role_id in [1, 3]:
        book = BookCopy.objects.get(id=copy_pk)

        input_data = f"http://127.0.0.1:8000/library/qr/search/{copy_pk}"
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(input_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white').convert('RGB')

        # Add text below QR code
        text = f"{book.barcode}"
        font_path = os.path.join(settings.BASE_DIR, 'arial.ttf')  # Make sure this font exists
        try:
            font = ImageFont.truetype(font_path, 12)
        except IOError:
            font = ImageFont.load_default()

        # Create a new image with extra height for text
        draw = ImageDraw.Draw(qr_img)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        total_height = qr_img.height + text_height + 10

        final_img = PilImage.new('RGB', (max(qr_img.width, text_width), total_height), 'white')
        final_img.paste(qr_img, (0, 0))
        draw = ImageDraw.Draw(final_img)
        draw.text(((final_img.width - text_width) // 2, qr_img.height + 5), text, fill='black', font=font)

        # Save the final image
        save_path = f'media/library/books/qr_code/{copy_pk}.jpeg'
        final_img.save(save_path)

        # Save to Django FileField
        filename = f'library/books/qr_code/{copy_pk}.jpeg'
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        with open(file_path, "rb") as file_object:
            file_m3u8 = File(file_object)
            book.qr_code.save(f'{copy_pk}.jpeg', file_m3u8)
            book.save()

        if book.qr_code:
            messages.success(request, 'Successfully created QR Code')
        else:
            messages.warning(request, "An error occurred, QR Code not created")

        return redirect('library:book_copies', pk=pk)

    else:
        messages.warning(request, "You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


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


def print_book_copies_qr_codes(request, pk):
    # Fetch student from database
    
    book = get_object_or_404(Book, id=pk)
    book_copies = book.copies.all()
    
    # Create a BytesIO buffer to store the PDF
    pdf_buffer = BytesIO()

    # Create response object with PDF content type
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="book_copies_{pk}.pdf"'

    # Set up ReportLab Document (A6 size in portrait mode)
    width, height = A4  # A6 size (105mm × 148mm)
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)

    elements = []  # List to store table data
    styles = getSampleStyleSheet()  # Load default styles for text formatting

    
    for book_copy in book_copies:
        
        if book_copy.qr_code:        
            
            try:
                logo_path = fetch_image_from_s3(f'media/{book_copy.qr_code.name}')
                try:           
                    logo_image = ImageReader(logo_path)
                    logo_img = Image(logo_path)
                    
                except requests.exceptions.RequestException:
                    logo_img = Paragraph("<b>[QR Code Missing]</b>", styles["Normal"])
                except Exception as e:
                    print(str(e))
                    
            except requests.exceptions.RequestException:
                logo_img = Paragraph("<b>[QR Code Missing]</b>", styles["Normal"])
                
            # Create a row with student photo and logo **side by side**
            image_table = Table(
                [[logo_img]],
                colWidths=[130]
            )
            image_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))

            # Add table to elements list
            elements.append(image_table)
            elements.append(Paragraph("<br/>", styles['Heading3'])) 

    # Build PDF
    doc.build(elements)
    
    # Save PDF to the Student model
    pdf_buffer.seek(0)
    book.book_copy_qr_codes.save(f"book_copies_{pk}.pdf", ContentFile(pdf_buffer.read()), save=True)

    messages.success(request,'Successfully created QR Code File')

    return redirect('library:book_copies',pk=pk)