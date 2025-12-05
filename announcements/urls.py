from django.urls import path

from students.views_student import student_dashboard
from . import views

app_name = 'announcements'

urlpatterns = [
    path('config/announcement/category/',views.AnnouncementCategoryListView.as_view(),name='config_announcement_categories'),
    path('config/announcement/category/add',views.add_announcement_category,name='add_announcement_category'),
    path('config/announcement/category/<int:pk>/edit/',views.edit_announcement_category,name='edit_announcement_category'),
    path('config/announcement/category/<int:pk>/delete/',views.delete_announcement_category,name='delete_announcement_category'),

    path('admin/',views.AnnouncementListView.as_view(),name='announcement_list'),
    path('admin/add',views.add_announcement,name='add_announcement'),
    path('admin/<int:pk>/edit/',views.edit_announcement,name='edit_announcement'),
    path('admin/<int:pk>/delete/',views.delete_announcement,name='delete_announcement'),

    path('admin/learning/programme/cohort/<int:pk>',views.CohortAnnouncementListView.as_view(),name='cohort_announcement_list'),
    path('admin/learning/programme/cohort/<int:pk>/add',views.add_cohort_announcement,name='add_cohort_announcement'),
    path('admin/learning/programme/cohort/<int:pk>/announcement/<int:announcement_pk>/edit/',views.edit_cohort_announcement,name='edit_cohort_announcement'),
    path('admin/learning/programme/cohort/<int:pk>/announcement/<int:announcement_pk>/delete/',views.delete_cohort_announcement,name='delete_cohort_announcement'),

     path('admin/learning/programme/cohort/registration/<int:pk>',views.CohortRegistrationAnnouncementListView.as_view(),name='cohort_registration_announcement_list'),
    path('admin/learning/programme/cohort/registration/<int:pk>/add',views.add_cohort_registration_announcement,name='add_cohort_registration_announcement'),
    path('admin/learning/programme/cohort/registration/<int:pk>/announcement/<int:announcement_pk>/edit/',views.edit_cohort_registration_announcement,name='edit_cohort_registration_announcement'),
    path('admin/learning/programme/cohort/registration/<int:pk>/announcement/<int:announcement_pk>/delete/',views.delete_cohort_registration_announcement,name='delete_cohort_registration_announcement'),
]