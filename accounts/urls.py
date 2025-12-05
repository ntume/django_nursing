from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

#password management

app_name = 'accounts'

urlpatterns = [
    path('login/user',views.login_user,name='login_user'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('register/',views.register,name='register'),
    path('password/expired',views.password_expired,name='password_expired'),
    path('password/renewal',views.renew_password,name='renew_password'),
    path('account/locked',views.account_locked,name='account_locked'),
    path('role_lookup/',views.role_lookup,name='role_lookup'),
    path('select/role/<int:pk>',views.select_role,name='select_role'),
    path('ajax/update/password',views.ajax_change_password,name='ajax_change_password'),
    path('user/forgot/password',views.forgot_password,name='forgot_password'),
    path('password/reset',views.select_new_password,name='select_new_password'),
    path('user/select/password',views.select_new_password,name='select_new_password'),
    path('user/save/password/<int:user_id>/<int:token_id>',views.selected_new_password,name='selected_new_password'),
    path('user/<int:pk>/change/password',views.change_password_first_login,name='change_password_first_login'),
    path('staff/<int:pk>/reset/password',views.reset_password_staff,name='reset_password_staff'),
]
