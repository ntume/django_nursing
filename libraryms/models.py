from django.db import models
import os
import uuid

from accounts.models import Role, User
# Create your models here.

def update_thumbnail_filename(instance, filename):
    path = "library/books/thumbnail/"
    ext = filename.split('.')[-1]
    format = "{}.{}".format(instance.id,ext)
    return os.path.join(path, format)


def update_qr_code_filename(instance, filename):
    path = "library/books/qrcode/"
    ext = filename.split('.')[-1]
    format = "{}.{}".format(instance.id,ext)
    return os.path.join(path, format)


class Author(models.Model):
    '''
    Author table
    '''

        
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Category(models.Model):
    '''
    Author table
    '''
     
    category = models.CharField(max_length=200)
    dewey_code = models.CharField(max_length=3,null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Book(models.Model):
    '''
    Book table
    '''
    
    class Meta:
        ordering = ['title']
     
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    authors = models.ManyToManyField(Author, related_name='books', through='BookAuthor')
    isbn = models.CharField(max_length=50,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to=update_thumbnail_filename,null=True)
    borrow_days = models.PositiveIntegerField(default=0)
    reserver_days = models.PositiveIntegerField(default=0)
    is_lendable = models.CharField(max_length=3,default='Yes')
    book_copy_qr_codes = models.FileField(upload_to=update_qr_code_filename,null=True)
    
    
    def is_available(self):
        book = Book.objects.get(id = self.id)
        return book.copies.filter(available = 'Yes').count()
    


class BookAuthor(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']



class Publisher(models.Model):
    '''
    Publisher
    '''
    
    class Meta:
        ordering = ['name']
    
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class BookCopy(models.Model):
    '''
    Book copies
    '''
    
    CHOICES = (('Yes','Yes'),('No','No'),('Hold','Hold'))
     
    book = models.ForeignKey(Book,on_delete=models.CASCADE,related_name='copies')
    year_published = models.CharField(max_length=4,blank=True,null=True)
    publisher = models.ForeignKey(Publisher,on_delete=models.SET_NULL,null=True,related_name='book_copies')
    barcode = models.CharField(max_length=50,null=True)
    available = models.CharField(max_length=10,default='Yes',choices=CHOICES)
    qr_code = models.FileField(upload_to=update_qr_code_filename,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edition = models.CharField(max_length=50,blank=True,null=True)    
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]  # or .hex[:12] for longer
        super().save(*args, **kwargs)
    
    
class CheckOut(models.Model):
    '''
    Book Checkouts
    '''
    
    CHOICE = (('Checked Out','Checked Out'),('Returned','Returned'),('Over Due','Over Due'))
     
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='book_checkouts')
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='book_checkouts')
    book_copy = models.ForeignKey(BookCopy,on_delete=models.CASCADE,related_name='checkouts')
    checkout_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True)
    status = models.CharField(max_length=20,default='Checked Out')
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Hold(models.Model):
    '''
    Book Checkouts
    '''
    
    CHOICE = (('Hold','Hold'),('Collected','Collected'),('Cancelled','Cancelled'))
      
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='book_holds')
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='book_holds')
    book_copy = models.ForeignKey(BookCopy,on_delete=models.CASCADE,related_name='book_holds')
    start = models.DateField()
    end = models.DateField()
    status = models.CharField(max_length=20,default='Hold')
    created_at = models.DateTimeField(auto_now_add=True)
    


class WaitingList(models.Model):
    '''
    Book Checkouts
    '''
    
    CHOICE = (('Waiting','Waiting'),('Collected','Collected'),('Cancelled','Cancelled'))
     
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='waiting_list')
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,related_name='waiting_list')
    book = models.ForeignKey(Book,on_delete=models.CASCADE,related_name='waiting_list')    
    status = models.CharField(max_length=20,default='Waiting')
    created_at = models.DateTimeField(auto_now_add=True)



class Notification(models.Model):
    '''
    Book Checkouts
    '''
    
    CHOICE = (('Hold','Hold'),('Waiting List','Waiting List'),('Return Due','Return Due'))
    
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='lms_notification')  
    notif_type = models.CharField(max_length=20,default='Waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class OnlineJournal(models.Model):
    '''
    Online Journals
    '''
    
    CHOICE = (('Hold','Hold'),('Waiting List','Waiting List'),('Return Due','Return Due'))
    
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='journals')  
    thumbnail = models.ImageField(upload_to=update_thumbnail_filename,null=True)
    title = models.TextField()
    url = models.URLField()
    publisher = models.ForeignKey(Publisher,on_delete=models.SET_NULL,null=True,related_name='journals')
    publication_type = models.CharField(max_length=20)
    access_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)