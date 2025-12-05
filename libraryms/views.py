from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q,F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.views.generic import ListView
from accounts.models import Role, User
import qrcode
import os
from django.conf import settings
from django.core.files import File
from azure.storage.blob import BlobServiceClient


from .models import *
from .forms import *
# Create your views here.


today = datetime.today()


class AuthorList(LoginRequiredMixin,ListView):
    template_name = 'library/authors.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(AuthorList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Author.objects.all().order_by('last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_menu'] = '--active'
        
        return context
    
    

@login_required()
def author_list_filter(request):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:
        
        author_list = Author.objects.all().order_by('last_name')

        if request.method == "POST":
            page = 1            
            
            if request.POST['first_name'] != "":
                author_list = author_list.filter(first_name__icontains = request.POST['first_name'])
            if request.POST['last_name'] != "":
                author_list = author_list.filter(last_name__icontains = request.POST['last_name'])
            
            filter = [request.POST['first_name'],request.POST['last_name']]
            filterstr = '-'.join(filter)

            paginator = Paginator(author_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "":
                    author_list = author_list.filter(first_name__icontains = filter[0])
                if filter[1] != "":
                    author_list = author_list.filter(last_name__icontains = filter[1])
                            
            paginator = Paginator(author_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        
        return render(request,'library/authors.html',{'items':items,'filter':filterstr,'author_menu_open':'side-menu__sub-open','author_menu':'--active' })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def author_add(request):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:

        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()            
            messages.success(request,"Successfully added Author")
        else:
            messages.warning(request,form.errors)

        return redirect('library:authors')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def author_edit(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        item_instance = Author.objects.get(id = pk)
        form = AuthorForm(request.POST,instance = item_instance)
        if form.is_valid():
            form.save()
        
            messages.success(request,"Successfully edited author")
        else:
            messages.warning(request,form.errors)

        return redirect('library:authors')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def author_delete(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        try:
            item_instance = Author.objects.get(id = pk)
            item_instance.delete()
            messages.success(request,"Successfully deleted author")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('library:authors')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class CategoryList(LoginRequiredMixin,ListView):
    template_name = 'library/categories.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CategoryList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Category.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_menu'] = '--active'
        
        return context

@login_required()
def category_add(request):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:

        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()            
            messages.success(request,"Successfully added Category")
        else:
            messages.warning(request,form.errors)

        return redirect('library:categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def category_edit(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        item_instance = Category.objects.get(id = pk)
        form = CategoryForm(request.POST,instance = item_instance)
        if form.is_valid():
            form.save()
        
            messages.success(request,"Successfully edited category")
        else:
            messages.warning(request,form.errors)

        return redirect('library:categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def category_delete(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        try:
            item_instance = Category.objects.get(id = pk)
            item_instance.delete()
            messages.success(request,"Successfully deleted category")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('library:categories')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class PublisherList(LoginRequiredMixin,ListView):
    template_name = 'library/publishers.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(PublisherList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Publisher.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publisher_menu'] = '--active'
        
        return context
    
    
@login_required()
def publisher_list_filter(request):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:
        
        publisher_list = Publisher.objects.all()

        if request.method == "POST":
            page = 1            
            
            if request.POST['name'] != "":
                publisher_list = publisher_list.filter(name__icontains = request.POST['name'])
            
            filter = [request.POST['name']]
            filterstr = '-'.join(filter)

            paginator = Paginator(publisher_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')

            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "":
                    publisher_list = publisher_list.filter(name__icontains = filter[0])
                            
            paginator = Paginator(publisher_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        
        return render(request,'library/publishers.html',{'items':items,'filter':filterstr,'publisher_menu_open':'side-menu__sub-open','publisher_menu':'--active' })
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def publisher_add(request):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:

        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()            
            messages.success(request,"Successfully added publisher")
        else:
            messages.warning(request,form.errors)

        return redirect('library:publishers')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def publisher_edit(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        item_instance = Publisher.objects.get(id = pk)
        form = PublisherForm(request.POST,instance = item_instance)
        if form.is_valid():
            form.save()
        
            messages.success(request,"Successfully edited publisher")
        else:
            messages.warning(request,form.errors)

        return redirect('library:publishers')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def publisher_delete(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        try:
            item_instance = Publisher.objects.get(id = pk)
            item_instance.delete()
            messages.success(request,"Successfully deleted publisher")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('library:publishers')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


class AdminBookList(LoginRequiredMixin,ListView):
    template_name = 'library/books.html'
    context_object_name = 'items'
    paginate_by = 20

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(AdminBookList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Book.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_menu'] = '--active'
        context['categories'] = Category.objects.all()
        context['authors'] = Author.objects.all().order_by('last_name')
        
        return context
    
    

@login_required()
def admin_book_list_filter(request):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:
        book_list = Book.objects.all()

        if request.method == "POST":
            page = 1           
            
            if request.POST['title'] != "":
                book_list = book_list.filter(title__icontains = request.POST['title'])
            if request.POST['category'] != "0":
                book_list = book_list.filter(category_id = request.POST['category'])
            if request.POST['author'] != "0":
                author = Author.objects.get(id = request.POST['author'])
                book_list = book_list.filter(authors__in = [author])
             
            filter = [request.POST['title'],request.POST['category'],request.POST['author']]
            filterstr = '-'.join(filter)

            paginator = Paginator(book_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')
            
            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "":
                    book_list = book_list.filter(title__icontains = filter[0])
                if filter[1]!= "0":
                    book_list = book_list.filter(category_id = filter[1])
                if filter[2] != "0":
                    author = Author.objects.get(id = filter[2])
                    book_list = book_list.filter(authors__in = [author])
            
            
            paginator = Paginator(book_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        authors= Author.objects.all().order_by('last_name')
        categories = Category.objects.all()
        
        return render(request,'library/books.html',{'items':items,
                                                    'filter':filterstr,
                                                    'book_menu':'--active',
                                                    'authors':authors,
                                                    'categories':categories,})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')


@login_required()
def book_add(request):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:

        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)  

            if 'category' in request.POST:
                book.category_id = request.POST['category']

            if 'isbn' in request.POST:
                book.isbn = request.POST['isbn']
                
            book.save()

            
            if not book.id:
                messages.error(request, "Error saving book. Please try again.")
                return redirect('library:books')

            authors = request.POST.getlist('authors[]')
            for s_id in authors:
                try:
                    author = Author.objects.get(id=s_id)
                    book.authors.add(author)
                except Author.DoesNotExist:
                    messages.warning(request, f"Author with id {s_id} does not exist.")  
                
            if 'thumbnail' in request.FILES:
                form_thumbnail = BookThumbnailForm(request.POST,request.FILES,instance=book)
                if form_thumbnail.is_valid():
                    form_thumbnail.save()
                    messages.success(request,'Successfully added thumbnail')
                else:
                    messages.warning(request,form_thumbnail.errors)
                  
            messages.success(request,"Successfully added book")
        else:
            messages.warning(request,form.errors)

        return redirect('library:books')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def book_edit(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        item_instance = Book.objects.get(id = pk)
        form = BookForm(request.POST,instance = item_instance)
        if form.is_valid():
            book = form.save(commit=False)  

            if 'category' in request.POST:
                book.category_id = request.POST['category']

            if 'isbn' in request.POST:
                book.isbn = request.POST['isbn']
                
            book.save()

            authors = request.POST.getlist('authors[]')
            for s_id in authors:
                author = Author.objects.get(id = s_id)
                book.authors.add(author)  
                
            if 'thumbnail' in request.FILES:
                form_thumbnail = BookThumbnailForm(request.POST,request.FILES,instance=book)
                if form_thumbnail.is_valid():
                    form_thumbnail.save()
                    messages.success(request,'Successfully added thumbnail')
                else:
                    messages.warning(request,form_thumbnail.errors)
        
            messages.success(request,"Successfully edited book")
        else:
            messages.warning(request,form.errors)

        return redirect('library:books')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def book_delete(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        try:
            item_instance = Book.objects.get(id = pk)
            item_instance.delete()
            messages.success(request,"Successfully deleted book")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('library:books')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def book_authors(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        book = Book.objects.get(id = pk)
        
        authors = request.POST.getlist('authors[]')
        for s_id in authors:
            author = Author.objects.get(id = s_id)
            book.authors.add(author)  
        
        messages.success(request,"Successfully added author")
        

        return redirect('library:books')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def book_author_delete(request,pk,author_pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        book = Book.objects.get(id = pk)
        author = Author.objects.get(id = author_pk)
        
        book.authors.remove(author)  
        
        messages.success(request,"Successfully removed author")
        

        return redirect('library:books')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    



    
class PatronBookList(LoginRequiredMixin,ListView):
    template_name = 'library/books_patron.html'
    context_object_name = 'items'
    paginate_by = 20

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(PatronBookList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Book.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_menu'] = '--active'
        context['authors'] = Author.objects.all()
        context['categories'] = Category.objects.all()
        
        return context
    
    

@login_required()
def patron_book_list_filter(request):

    if request.user.logged_in_role_id == 10:
        book_list = Book.objects.all()

        if request.method == "POST":
            page = 1           
            
            if request.POST['title'] != "":
                book_list = book_list.filter(title__icontains = request.POST['title'])
            if request.POST['category'] != "0":
                book_list = book_list.filter(category_id = request.POST['category'])
            if request.POST['author'] != "0":
                author = Author.objects.get(id = request.POST['author'])
                book_list = book_list.filter(authors__in = [author])
             
            filter = [request.POST['title'],request.POST['category'],request.POST['author']]
            filterstr = '-'.join(filter)

            paginator = Paginator(book_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')
            
            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "":
                    book_list = book_list.filter(title__icontains = filter[0])
                if filter[1]!= "0":
                    book_list = book_list.filter(category_id = filter[1])
                if filter[2] != "0":
                    author = Author.objects.get(id = filter[2])
                    book_list = book_list.filter(authors__in = [author])
            
            
            paginator = Paginator(book_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        authors = Author.objects.all()
        categories = Category.objects.all()
        return render(request,'library/books_patron.html',{'items':items,
                                                           'filter':filterstr,
                                                           'book_menu':'--active',
                                                           'categories':categories,
                                                           'authors':authors})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def patron_book_hold(request,pk):
    '''
    Function for patron to hold a book
    '''   
    
    if request.user.logged_in_role_id == 10:
        
        #check if student holding book
        check_hold_active = Hold.objects.filter(user = request.user,
                                                book_copy__book_id = pk,
                                                status = 'Hold').exists()
        
        if check_hold_active:
            messages.warning(request,'You currently have a hold on this book, please borrow it within 24 hours')
        else:        
            #check if there is still a copy left to hold
            check_copy = BookCopy.objects.filter(book_id = pk,available='Yes')
            if check_copy.exists():
                copy = check_copy.first()
                
                hold = Hold.objects.create(
                    user = request.user,
                    role  = request.user.logged_in_role,
                    book_copy = copy,
                    start = today,
                    end = today + timedelta(days=copy.book.reserver_days),
                )
                
                copy.available = 'On Hold'
                copy.save()
                
                messages.success(request,'Successfully placed book on hold, you have 24 hours to collect the book')
                
            else:
                messages.warning(request,'Sorry there are no copies left to hold.')
            
        return redirect('library:patron_book_list')            
        
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    


@login_required()
def patron_book_waiting_list(request,pk):
    '''
    Function for patron to waiting list for a book
    '''   
    
    if request.user.logged_in_role_id == 10:
        
       
        #check if there is still a copy left to hold
        
        check_copy = BookCopy.objects.filter(book_id = pk,available='Yes')
        if check_copy.exists():
            messages.warning(request,'There is an available copy, you may come collect it or place it onhold for 24 hours.')
            
        else:
            #check if copy is onhold
            check_copy_onhold = Hold.objects.filter(book_copy__book_id = pk,status='Hold',user=request.user)
            if check_copy_onhold.exists():
                onhold = check_copy_onhold.first()
                messages.warning(request,f'You currently have this book on hold, please collect it by {onhold.end}')
            else:
                #check if on waiting list
                waiting_check = WaitingList.objects.filter(user = request.user,book_id = pk,status='Waiting')
                if waiting_check.exists():
                    messages.warning(request,'You are on the waiting list for this book')
                else:
                    
                    waiting = WaitingList.objects.create(user = request.user,
                                                         role = request.user.logged_in_role,
                                                         book_id = pk,
                                                         status='Waiting')
                    messages.success(request,'You have been added to the waiting list for this book')
            
            
        return redirect('library:patron_book_list')            
        
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
     
class BookCopyList(LoginRequiredMixin,ListView):
    template_name = 'library/book_copies.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(BookCopyList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  BookCopy.objects.filter(book_id = self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_menu'] = '--active'
        context['book'] = Book.objects.get(id = self.kwargs['pk'])
        context['publishers'] = Publisher.objects.all()
        context['users'] = User.objects.all()
        context['today'] = today
        
        return context

@login_required()
def book_copy_add(request,pk):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:

        form = BookCopyForm(request.POST)
        if form.is_valid():
            book_copy = form.save(commit=False) 
            
            book_copy.book_id = pk 

            if 'publisher' in request.POST:
                book_copy.publisher_id = request.POST['publisher']
            
            book_copy.save()   
            
            #create barcode: DeweyDecimalCode-1st 3 letters of title-slug
            author_surname = ''
            title = book_copy.book.title[0:3]
            author = book_copy.book.authors.first()
            if author:
                author_surname = author.last_name[0:3]
            
            if book_copy.book.category:
                ddc = book_copy.book.category.dewey_code
            else:
                ddc = None
                
            if book_copy.slug != "":
                slug = book_copy.slug
            else:
                slug = uuid.uuid4().hex[:8]
                book_copy.slug = slug
                
            book_copy.barcode = f'{ddc}-{author_surname}-{slug}'
            book_copy.save()               
                  
            messages.success(request,"Successfully added book copy")
        else:
            messages.warning(request,form.errors)

        return redirect('library:book_copies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def book_copy_edit(request,pk,copy_pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        item_instance = BookCopy.objects.get(id = copy_pk)
        form = BookCopyForm(request.POST,instance = item_instance)
        if form.is_valid():
            copy = form.save(commit=False) 
            
            if 'publisher' in request.POST:
                copy.publisher_id = request.POST['publisher']

            if 'barcode' in request.POST:
                copy.barcode = request.POST['barcode']

            copy.save() 
        
            messages.success(request,"Successfully edited book copy")
        else:
            messages.warning(request,form.errors)

        return redirect('library:book_copies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def book_copy_delete(request,pk,copy_pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        try:
            item_instance = BookCopy.objects.get(id = copy_pk)
            item_instance.delete()
            messages.success(request,"Successfully deleted book copy")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('library:book_copies',pk=pk)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')






@login_required()
def book_copy_check_out(request,pk):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:
        
        copy = BookCopy.objects.get(id = pk)      
            
        form = CheckOutForm(request.POST)
        if form.is_valid():
            checkout = form.save(commit=False) 
            checkout.user_id = request.POST['user']
            checkout.book_copy = copy
            checkout.checkout_date = request.POST['checkout_date']
            checkout.save()
            checkout.due_date = checkout.checkout_date + timedelta(days=copy.book.borrow_days),
                                
            checkout.save()
                        
            copy.available = 'No'
            copy.save()
                
            messages.success(request,"Successfully checked out book")
        else:
            messages.warning(request,form.errors)

        return redirect('library:book_copies',pk=copy.book_id)
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
class CheckoutList(LoginRequiredMixin,ListView):
    template_name = 'library/checkout.html'
    context_object_name = 'items'
    paginate_by = 20

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(CheckoutList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  CheckOut.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['check_out_menu'] = '--active'
        context['today'] = today
        
        return context
    
    
@login_required()
def check_out_list_filter(request):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:
        book_list = CheckOut.objects.all()

        if request.method == "POST":
            page = 1           
            
            if request.POST['title'] != "":
                book_list = book_list.filter(book_copy__book__title__icontains = request.POST['title'])
           
            if request.POST['name'] != "":
                book_list = book_list.filter(Q(user__first_name__icontains = request.POST['name'])|
                                             Q(user__last_name__icontains = request.POST['name']))
                
            if request.POST['status'] != "0":
                book_list = book_list.filter(status = request.POST['status'] )
             
            filter = [request.POST['title'],request.POST['name'],request.POST['status'] ]
            filterstr = '-'.join(filter)

            paginator = Paginator(book_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')
            
            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "":
                    book_list = book_list.filter(book_copy__book__title__icontains = filter[0])
                
                if filter[1] != "":
                    book_list = book_list.filter(Q(user__first_name__icontains = filter[1])|
                                             Q(user__last_name__icontains = filter[1]))
                    
                if filter[2] != "0":
                    book_list = book_list.filter(status = filter[2] )
            
            
            paginator = Paginator(book_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        authors= Author.objects.all()
        categories = Category.objects.all()
    
        
        return render(request,'library/checkout.html',{'items':items,
                                                    'filter':filterstr,
                                                    'check_out_menu':'--active',
                                                    'authors':authors,
                                                    'today':today,
                                                    'categories':categories,})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

 
@login_required()
def check_out_returned(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        book_checkout = CheckOut.objects.get(id = pk)
        book_checkout.status = 'Returned'
        book_checkout.return_date = request.POST['return_date']
        book_checkout.save()
        
        messages.success(request,"Successfully returned book")
        
        return redirect('library:check_out_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

class PatronBookWaitingList(LoginRequiredMixin,ListView):
    template_name = 'library/patron_waiting_list.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(PatronBookWaitingList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  WaitingList.objects.filter(user = self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_menu'] = '--active'
        context['authors'] = Author.objects.all()
        context['categories'] = Category.objects.all()
        
        return context
 


class PatronBookOnHoldList(LoginRequiredMixin,ListView):
    template_name = 'library/patron_hold.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 10:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(PatronBookOnHoldList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Hold.objects.filter(user = self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_menu'] = '--active'
        context['authors'] = Author.objects.all()
        context['categories'] = Category.objects.all()
        
        return context
    
    
    
class AdminBookWaitingList(LoginRequiredMixin,ListView):
    template_name = 'library/waiting_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(AdminBookWaitingList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  WaitingList.objects.filter(status = 'Waiting')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_waiting_list_menu'] = '--active'
        context['categories'] = Category.objects.all()
        context['authors'] = Author.objects.all()
        context['today'] = today
        
        return context
    
    

@login_required()
def admin_book_waiting_list_filter(request):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:
        book_list = WaitingList.objects.all()

        if request.method == "POST":
            page = 1           
            
            if request.POST['title'] != "":
                book_list = book_list.filter(book__title__icontains = request.POST['title'])
            if request.POST['category'] != "0":
                book_list = book_list.filter(book__category_id = request.POST['category'])
            if request.POST['author'] != "0":
                author = Author.objects.get(id = request.POST['author'])
                book_list = book_list.filter(book__authors__in = [author])
            if request.POST['name'] != "":
                book_list = book_list.filter(Q(user__first_name__icontains = request.POST['name'])|
                                             Q(user__last_name__icontains = request.POST['name']))
             
            filter = [request.POST['title'],request.POST['category'],request.POST['author'],request.POST['name']]
            filterstr = '-'.join(filter)

            paginator = Paginator(book_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')
            
            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "":
                    book_list = book_list.filter(book__title__icontains = filter[0])
                if filter[1]!= "0":
                    book_list = book_list.filter(book__category_id = filter[1])
                if filter[2] != "0":
                    author = Author.objects.get(id = filter[2])
                    book_list = book_list.filter(book__authors__in = [author])
                if filter[3] != "":
                    book_list = book_list.filter(Q(user__first_name__icontains = filter[3])|
                                             Q(user__last_name__icontains = filter[3]))
            
            
            paginator = Paginator(book_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        authors= Author.objects.all()
        categories = Category.objects.all()
        
        
        
        return render(request,'library/waiting_list.html',{'items':items,
                                                    'filter':filterstr,
                                                    'book_waiting_list_menu':'--active',
                                                    'authors':authors,
                                                    'today':today,
                                                    'categories':categories,})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
class AdminBookHoldList(LoginRequiredMixin,ListView):
    template_name = 'library/hold_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(AdminBookHoldList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  Hold.objects.filter(status = 'Hold')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_hold_list_menu'] = '--active'
        context['categories'] = Category.objects.all()
        context['authors'] = Author.objects.all()
        context['today'] = today
        
        return context
    
    

@login_required()
def admin_book_on_hold_list_filter(request):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:
        book_list = Hold.objects.all()

        if request.method == "POST":
            page = 1           
            
            if request.POST['title'] != "":
                book_list = book_list.filter(book_copy__book__title__icontains = request.POST['title'])
            if request.POST['category'] != "0":
                book_list = book_list.filter(book_copy__book__category_id = request.POST['category'])
            if request.POST['author'] != "0":
                author = Author.objects.get(id = request.POST['author'])
                book_list = book_list.filter(book_copy__book__authors__in = [author])
            if request.POST['name'] != "":
                book_list = book_list.filter(Q(user__first_name__icontains = request.POST['name'])|
                                             Q(user__last_name__icontains = request.POST['name']))
             
            filter = [request.POST['title'],request.POST['category'],request.POST['author'],request.POST['name']]
            filterstr = '-'.join(filter)

            paginator = Paginator(book_list, 20)

            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        if request.method == "GET":
            page = request.GET.get('page', 1)
            filterstr = request.GET.get('filter')
            
            if filterstr and filterstr != 'None':
                filter = filterstr.split('-')

                if filter[0] != "":
                    book_list = book_list.filter(book_copy__book__title__icontains = filter[0])
                if filter[1]!= "0":
                    book_list = book_list.filter(book_copy__book__category_id = filter[1])
                if filter[2] != "0":
                    author = Author.objects.get(id = filter[2])
                    book_list = book_list.filter(book_copy__book__authors__in = [author])
                if filter[3] != "":
                    book_list = book_list.filter(Q(user__first_name__icontains = filter[3])|
                                             Q(user__last_name__icontains = filter[3]))
            
            
            paginator = Paginator(book_list, 20)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        authors= Author.objects.all()
        categories = Category.objects.all()
        
        return render(request,'library/hold_list.html',{'items':items,
                                                    'filter':filterstr,
                                                    'book_hold_list_menu':'--active',
                                                    'authors':authors,
                                                    'today':today,
                                                    'categories':categories,})
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
@login_required()
def book_copy_hold_check_out(request,pk):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:
        
        hold = Hold.objects.get(id = pk)
        copy = hold.book_copy        
            
        form = CheckOutForm(request.POST)
        if form.is_valid():
            checkout = form.save(commit=False) 
            checkout.user = hold.user
            checkout.role = hold.role
            checkout.book_copy = copy
            checkout.checkout_date = request.POST['checkout_date']
            checkout.save()
            checkout.due_date = checkout.checkout_date + timedelta(days=copy.book.borrow_days),
                            
            checkout.save()
            
            hold.status = 'Collected'
            hold.save()
            
            copy.available = 'No'
            copy.save()
                
            messages.success(request,"Successfully checked out book")
        else:
            messages.warning(request,form.errors)

        return redirect('library:admin_book_on_hold_list')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
class AdminOnlineJournalList(LoginRequiredMixin,ListView):
    template_name = 'library/admin_online_journal.html'
    context_object_name = 'items'

    def get(self, *args, **kwargs):
        if self.request.user.logged_in_role_id != 3 and self.request.user.logged_in_role_id != 1:
            messages.warning(self.request,"You do not have rights to that portion of the site, you have been logged off!")
            return redirect('accounts:logout')
        return super(AdminOnlineJournalList, self).get(*args, **kwargs)

    def get_queryset(self):
        return  OnlineJournal.objects.all().order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['online_journal_menu'] = '--active'
        context['publishers'] = Publisher.objects.all()
        
        return context
    
@login_required()
def online_journal_add(request):

    if request.user.logged_in_role_id == 1 or request.user.logged_in_role_id == 3:

        form = OnlineJournalForm(request.POST)
        if form.is_valid():
            journal = form.save(commit=False)
            if 'publisher' in request.POST:
                journal.publisher_id = request.POST['publisher']

            journal.user = request.user
                
            journal.save()
            
            if 'thumbnail' in request.FILES:
                form_thumb =  OnlineJournalThumbnailForm(request.POST,request.FILES,instance=journal)
                if form_thumb.is_valid():
                     form_thumb.save()
                     messages.success(request,'Successfully added Thumbnail')
                else:
                    messages.warning(request,form_thumb.errors)
                    
            messages.success(request,"Successfully added Online Journal")
        else:
            messages.warning(request,form.errors)

        return redirect('library:admin_online_journals')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def online_journal_edit(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        item_instance = OnlineJournal.objects.get(id = pk)
        form = OnlineJournalForm(request.POST,instance = item_instance)
        if form.is_valid():
            journal = form.save(commit=False)
            if 'publisher' in request.POST:
                journal.publisher_id = request.POST['publisher']
                
            journal.user = request.user
            journal.save()
            
            if 'thumbnail' in request.FILES:
                form_thumb =  OnlineJournalThumbnailForm(request.POST,request.FILES,instance=journal)
                if form_thumb.is_valid():
                     form_thumb.save()
                     messages.success(request,'Successfully added Thumbnail')
                else:
                    messages.warning(request,form_thumb.errors)
        
            messages.success(request,"Successfully edited Online Journal")
        else:
            messages.warning(request,form.errors)

        return redirect('library:admin_online_journals')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

@login_required()
def online_journal_delete(request,pk):

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 1:

        try:
            item_instance = OnlineJournal.objects.get(id = pk)
            item_instance.delete()
            messages.success(request,"Successfully deleted Online Journal")
        except Exception as e:
            messages.warning(request,f"An error has occurred, please try again - Error: {str(e)}")

        return redirect('library:admin_online_journals')
    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    
    
class PatronOnlineJournalList(LoginRequiredMixin,ListView):
    template_name = 'library/patron_online_journals.html'
    context_object_name = 'items'
    
    def get_queryset(self):
        return  OnlineJournal.objects.all().order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['online_journal_menu'] = '--active'
        context['publishers'] = Publisher.objects.all()
        
        return context