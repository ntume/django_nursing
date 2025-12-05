from tempfile import NamedTemporaryFile
from library.models import Book
import qrcode
import os

from PIL import Image as PilImage
from PIL import ImageFont, ImageDraw 

from datetime import timedelta
import uuid
from django.conf import settings
from django.core.files import File
from pdfrw import PdfReader, PdfWriter, IndirectPdfDict
from .models import AssessorModeratorApplication
from azure.storage.blob import BlobServiceClient
from io import BytesIO

def fetch_image_from_blob(image_name):
    # Use the connection string from settings
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
    
    # Get the media container name from settings
    container_name = 'media'
    
    # Get the BlobClient
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=image_name)
    
    # Download the blob (image) content as a byte stream
    downloaded_blob = blob_client.download_blob().readall()
    
    # Save the image to a temporary file
    temp_image = NamedTemporaryFile(delete=False, suffix=".png")  # or .jpg, .jpeg depending on your image type
    temp_image.write(downloaded_blob)
    temp_image.flush()
    
    return temp_image.name


def print_qr_code(request,pk):
    '''
    Function to create the QR Code
    '''
    
    book = Book.objects.get(id=pk)
                        
    input_data = f"http://127.0.0.1:8000/library/qr/search/{ pk }"
    #Creating an instance of qrcode
    qr = qrcode.QRCode(
    version=1,
    box_size=4,
    border=1)
    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(f'media/library/book/qr_code/{pk}.jpeg')
    
    filename = f'library/book/qr_code/{pk}.jpeg'
    
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        
    with open(file_path, "rb") as file_object:
        file_m3u8 = File(name='qr_code.jpeg', file=file_object)            
        book.qr_code.save('qr_code.jpeg', file_m3u8)
        book.save()              

    messages.succ

    return redirect('library:books') 

