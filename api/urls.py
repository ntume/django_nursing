from django.urls import path
from . import views
from . import views

app_name = 'api'

urlpatterns = [
    path('student/<int:pk>/<slug:slug>/onboarding/<int:page>',views.open_onboarding,name='open_onboarding'),
    path('student/<int:pk>/onboarding/learner/details',views.edit_learner_programme_details,name='edit_learner_programme_details'),
    path('student/<int:pk>/onboarding/address',views.edit_learner_address_details,name='edit_learner_address_details'),
    path('student/<int:pk>/onboarding/education',views.edit_learner_education_details,name='edit_learner_education_details'),
    path('student/<int:pk>/onboarding/kin',views.edit_learner_next_of_kin_details,name='edit_learner_next_of_kin_details'),
    path('student/<int:pk>/nextofkin/add',views.add_profile_next_of_kin_details,name='add_profile_next_of_kin_details'),
    path('student/<int:pk>/nextofkin/<int:next_of_kin_pk>/edit',views.edit_profile_next_of_kin_details,name='edit_profile_next_of_kin_details'),
    path('student/<int:pk>/nextofkin/<int:next_of_kin_pk>/delete',views.delete_profile_next_of_kin_details,name='delete_profile_next_of_kin_details'),
    path('student/<int:pk>/onboarding/submit',views.submit_onboarding_details,name='submit_onboarding_details'),
    path('student/registration/verification/<slug:pk>/verification',views.confirm_learner_pop,name='confirm_learner_pop'),   
    
]