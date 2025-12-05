from django.urls import path,include
from . import views

app_name = 'adverts'

urlpatterns = [
    path('',views.AdvertList.as_view(),name='advertlist'),
]
