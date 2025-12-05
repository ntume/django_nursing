from django.urls import path

from libraryms.print_qr_code import book_copy_print_qr_code, print_book_copies_qr_codes
from . import views

app_name = 'library'

urlpatterns = [
    path('admin/authors',views.AuthorList.as_view(),name='authors'),
    path('admin/authors/filter',views.author_list_filter,name='author_list_filter'),
    path('admin/authors/add',views.author_add,name='author_add'),
    path('admin/authors/<int:pk>/edit',views.author_edit,name='author_edit'),
    path('admin/authors/<int:pk>/delete',views.author_delete,name='author_delete'),
    path('admin/categories',views.CategoryList.as_view(),name='categories'), 
    path('admin/categories/add',views.category_add,name='category_add'),
    path('admin/categories/<int:pk>/edit',views.category_edit,name='category_edit'),
    path('admin/categories/<int:pk>/delete',views.category_delete,name='category_delete'),
    path('admin/publishers',views.PublisherList.as_view(),name='publishers'), 
    path('admin/publishers/filter',views.publisher_list_filter,name='publisher_list_filter'),
    path('admin/publishers/add',views.publisher_add,name='publisher_add'),
    path('admin/publishers/<int:pk>/edit',views.publisher_edit,name='publisher_edit'),
    path('admin/publishers/<int:pk>/delete',views.publisher_delete,name='publisher_delete'),
    path('admin/books',views.AdminBookList.as_view(),name='books'), 
    path('admin/books/filter',views.admin_book_list_filter,name='admin_book_list_filter'), 
    path('admin/books/add',views.book_add,name='book_add'),
    path('admin/books/<int:pk>/edit',views.book_edit,name='book_edit'),
    path('admin/books/<int:pk>/delete',views.book_delete,name='book_delete'),
    
    path('admin/book/<int:pk>/copies',views.BookCopyList.as_view(),name='book_copies'),  
    path('admin/books/<int:pk>/copies/add',views.book_copy_add,name='book_copy_add'),
    path('admin/books/<int:pk>/copies/<int:copy_pk>/edit',views.book_copy_edit,name='book_copy_edit'),
    path('admin/books/<int:pk>/copies/<int:copy_pk>/delete',views.book_copy_delete,name='book_copy_delete'),
    path('admin/books/<int:pk>/copies/<int:copy_pk>/print/qrcode',book_copy_print_qr_code,name='book_copy_print_qr_code'),
    path('admin/books/<int:pk>/copies/create/qrcode/file',print_book_copies_qr_codes,name='print_book_copies_qr_codes'),
    
    path('admin/books/copy/<int:pk>/check/out',views.book_copy_check_out,name='book_copy_check_out'),
    
    path('admin/books/<int:pk>/authors',views.book_authors,name='book_authors'),
    path('admin/books/<int:pk>/authors/<int:author_pk>',views.book_author_delete,name='book_author_delete'),
    path('patron/books',views.PatronBookList.as_view(),name='patron_book_list'), 
    path('patron/books/filter',views.patron_book_list_filter,name='patron_book_list_filter'), 
    path('patron/books/<int:pk>/hold',views.patron_book_hold,name='patron_book_hold'), 
    path('patron/books/<int:pk>/waiting/list',views.patron_book_waiting_list,name='patron_book_waiting_list'),
    
    path('patron/books/waiting/list',views.PatronBookWaitingList.as_view(),name='patron_book_waiting_list'), 
    path('patron/books/hold/list',views.PatronBookOnHoldList.as_view(),name='patron_book_hold_list'), 
    
    path('admin/books/waiting/list',views.AdminBookWaitingList.as_view(),name='admin_book_waiting_list'), 
    path('admin/books/waiting/list/filter',views.admin_book_waiting_list_filter,name='admin_book_waiting_list_filter'), 
    
    path('admin/books/hold/list',views.AdminBookHoldList.as_view(),name='admin_book_on_hold_list'), 
    path('admin/books/hold/list/filter',views.admin_book_on_hold_list_filter,name='admin_book_on_hold_list_filter'),
    path('admin/books/hold/<int:pk>/checkout',views.book_copy_hold_check_out,name='book_copy_hold_check_out'),
    
    path('admin/books/checkout/list',views.CheckoutList.as_view(),name='check_out_list'), 
    path('admin/books/checkout/list/filter',views.check_out_list_filter,name='check_out_list_filter'),
    path('admin/books/checkout/<int:pk>/returned',views.check_out_returned,name='check_out_returned'),
    
    path('admin/online/resource',views.AdminOnlineJournalList.as_view(),name='admin_online_journals'), 
    path('admin/online/resource/add',views.online_journal_add,name='online_journal_add'),
    path('admin/online/resource/<int:pk>/edit',views.online_journal_edit,name='online_journal_edit'),
    path('admin/online/resource/<int:pk>/delete',views.online_journal_delete,name='online_journal_delete'),
    path('patron/online/resource',views.PatronOnlineJournalList.as_view(),name='patron_online_journals'),
]