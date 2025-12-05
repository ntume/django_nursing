import re
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from datetime import datetime, date, timedelta
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.conf import settings
from college.models import Staff
from django_htmx.http import HttpResponseClientRedirect
from django_nursing.decorators import login_limit
from django.core.cache import cache
import random
import os
from configurable.models import Country, Disability, EmploymentEconomicStatus, Gender, Language, Province, Race, Suburb, TypeOfID
from django_nursing.settings import LOGIN_RATE_LIMIT

from .models import *
from .forms import *

from django_nursing.email_functions import BackgroundThreadSendEmail, send_email_activation_external,send_email_forgot_password, send_email_rest_password
from za_id_number.za_id_number import SouthAfricanIdentityValidate

# Create your views here.

def password_gen(passlen):
    s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?[]"
    password =  "".join(random.sample(s,passlen ))
    return password

def number_gen(passlen):
    s = "0123456789"
    password =  "".join(random.sample(s,passlen ))
    return password

def password_validator(password):
    message = ''
    valid = True
    if not re.findall('\d', password):
        message = message + "Your password must contain at least 1 digit, 0-9.<br>"
        valid = False

    if not re.findall('[A-Z]', password):
        message = message + "Your password must contain at least 1 uppercase letter, A-Z.<br>"
        valid = False

    if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
        message = message + "Your password must contain at least 1 special character: ()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?<br>"
        valid = False
    if len(password) < 14:
        message = message + "Your password must be at least 14 characters long<br>"
        valid = False

    return valid, message


def role_lookup(request):
  
    if request.user.is_authenticated:

        if request.user.password_change_date:
            days_between = date.today() - request.user.password_change_date

            if days_between.days >= 42:
                return redirect('accounts:password_expired') 

        roles = request.user.roles.all()

        if roles.exists():
           
            if roles.count() > 1:                
                return render(request,'accounts/choose_role.html',{'roles':roles})

            elif roles.count() == 1:
                role = roles.first()
            else:                
                messages.warning(request,"Your user account currently doesn't have a role assigned to it, please register a new role")
                return redirect('accounts:logout')

            request.user.logged_in_role = role
            request.user.save()


            if request.user.logged_in_role_id == 1:
                messages.success(request,'Successfully logged in')
                return redirect('administration:dashboard_principal')

            elif request.user.logged_in_role_id == 2:
                messages.success(request,'Successfully logged in')
                return redirect('/administration/')
            
            elif request.user.logged_in_role_id == 3:
                messages.success(request,'Successfully logged in')
                return redirect('administration:dashboard_librarian')
            
            elif request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
                messages.success(request,'Successfully logged in')
                return redirect('administration:dashboard_lecturer')
            
            elif request.user.logged_in_role_id == 6:
                messages.success(request,'Successfully logged in')
                return redirect('administration:dashboard_programme_coordinator')
            
            elif request.user.logged_in_role_id == 7:
                messages.success(request,'Successfully logged in')
                return redirect('college:moderator_dashboard')

            elif request.user.logged_in_role_id == 10:
                messages.success(request,'Successfully logged in')
                return redirect('students:student_dashboard')
            
            elif request.user.logged_in_role_id == 11:
                messages.success(request,'Successfully logged in')
                return redirect('college:facility_hod_dashboard')
            
            elif request.user.logged_in_role_id == 12:
                messages.success(request,'Successfully logged in')
                return redirect('college:co_assessor_dashboard')

        else:
            messages.warning(request,"Your user account currently doesn't have a role assigned to it, please register a new role")
            return redirect('accounts:logout')             
    else:        
        return redirect('accounts:login_user')


def select_role(request,pk):
    '''
    Select role to log on
    '''

    role = Role.objects.get(id = pk)
    user = request.user
    user.logged_in_role = role
    user.save()

    if request.user.logged_in_role_id == 1:
        messages.success(request,'Successfully logged in')
        return redirect('administration:dashboard_principal')

    elif request.user.logged_in_role_id == 2:
        messages.success(request,'Successfully logged in')
        return redirect('/administration/')
    
    elif request.user.logged_in_role_id == 3:
        messages.success(request,'Successfully logged in')
        return redirect('administration:dashboard_librarian')
    
    elif request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
        messages.success(request,'Successfully logged in')
        return redirect('administration:dashboard_lecturer')
    
    elif request.user.logged_in_role_id == 6:
        messages.success(request,'Successfully logged in')
        return redirect('administration:dashboard_programme_coordinator')
    
    elif request.user.logged_in_role_id == 7:
        messages.success(request,'Successfully logged in')
        return redirect('college:moderator_dashboard')

    elif request.user.logged_in_role_id == 10:
        messages.success(request,'Successfully logged in')
        return redirect('students:student_dashboard')
    
    elif request.user.logged_in_role_id == 11:
        messages.success(request,'Successfully logged in')
        return redirect('college:facility_hod_dashboard')
    
    elif request.user.logged_in_role_id == 12:
        messages.success(request,'Successfully logged in')
        return redirect('college:co_assessor_dashboard')

    else:
        messages.warning(request,"Sorry, requested role does not exist")
        return redirect('accounts:login_user')

@login_limit
def login_user(request):
    
    next = ""

    if request.GET:  
        next = request.GET['next']
   
    if request.user.is_authenticated:
        if request.user.password_change_date:
            days_between = date.today() - request.user.password_change_date

            if days_between.days >= 42:
                return redirect('accounts:password_expired')       
        return redirect('accounts:role_lookup')

    if request.method == 'POST':

        valid_captcha = True

        if settings.DEBUG == True:
            valid_captcha = True            
        else:
            form_recaptcha = ReCaptchaForm(request.POST) 
            if form_recaptcha.is_valid():
                valid_captcha = True
            else:
                valid_captcha = True
        
        if valid_captcha:
            username = request.POST['username'].lower()
            password = request.POST['password']

            check_user = User.objects.filter(email__iexact = username)          
            
            if check_user.exists():

                last_login = check_user.first().last_login
                
                user = authenticate(request, username=username, password=password)
            
                if user is not None:
            
                    login(request, user)

                    # Reset login attempts on successful login
                    cache.delete(f'login_attempts_{username}')

                    if next == "":
                        todays_date = date.today()

                        if user.password_change_date:
                            days_between = todays_date - user.password_change_date

                            if days_between.days >= 42:
                                return redirect('accounts:password_expired')
                                        
                        
                        return redirect('accounts:role_lookup')
                    else:
                        return redirect(next)
                    
                else:
                    messages.warning(request, 'The provided credentials are incorrect; please try again')               
            else:
                messages.warning(request, 'The provided credentials are incorrect; please try again')
        else:
            messages.warning(request,"You must pass the reCAPTCHA test")

    form_recaptcha = ReCaptchaForm()       
    return render(request,'accounts/login.html',{'form_recaptcha':form_recaptcha})


@login_required()
def password_expired(request):

    return render(request,'accounts/expired_password.html')


@login_required()
def renew_password(request):

    '''
    Function to change expired password
    '''

    if request.method == "POST":
        password = request.POST['new_password1']
        password2 = request.POST['new_password2']

        if password == password2:
            #check if same as old password
            if not request.user.check_password(password):
                valid_pass, message_password = password_validator(password)

                if valid_pass:
                    user = request.user
                    user.set_password(password)
                    user.password_change_date = date.today()
                    user.save()
                    messages.success(request,'Successfully updated your password, please login using your new password')
        
                    return HttpResponse('<div><meta http-equiv="refresh" content="0; url=/accounts/logout"></div>')
                else:
                    messages.warning(request,'The password supplied does not meet the security requirements of the LMS')
                    messages.warning(request,message_password)
                    return render(request,'messages.html')
            else:
                messages.warning(request,'Sorry the new password cannot be the same as your previous password. Please try again')
                return render(request,'messages.html') 
        else:
            messages.warning(request,'Sorry the two passwords do not match. Please try again')
            return render(request,'messages.html')

    return render(request,'accounts/expired_password.html')


def register(request):
    
    #password = password_gen(8)
    
    if request.method == "POST":

        form_recaptcha = ReCaptchaForm(request.POST) 
        if form_recaptcha.is_valid():

            #check if valid SA ID if SA ID Type selected

            if 'type_of_id'in request.POST and request.POST['type_of_id'] == "5":
                id_number = request.POST['id_number']
                id_validation = SouthAfricanIdentityValidate(id_number)
                if not id_validation.validate():
                    
                    messages.warning(request,'Sorry the ID supplied is not a valid South African ID. Please try again')
                    form_recaptcha = ReCaptchaForm() 
                    return render(request,'accounts/messages.html',{'form_recaptcha':form_recaptcha})


            role = Role.objects.get(id = request.POST['role'])
            
            found = False
            assessor_found = False
            found_message = ''
            msg_register = ''

            password = request.POST['password']
            password2 = request.POST['password2']

            if password == password2:
                valid_pass, message_password = password_validator(password)

            else:
                messages.warning(request,'Sorry the two passwords do not match. Please try again')
                form_recaptcha = ReCaptchaForm() 
                return render(request,'accounts/messages.html',{'form_recaptcha':form_recaptcha})
                
        else:
            messages.warning(request,"You must pass the reCAPTCHA test")
            form_recaptcha = ReCaptchaForm() 
            return render(request,'accounts/messages.html',{'form_recaptcha':form_recaptcha})
            
    
    roles = Role.objects.filter(internal = 'No')
    form_recaptcha = ReCaptchaForm() 
    return render(request,'accounts/register.html',{'roles':roles,'form_recaptcha':form_recaptcha})


def account_locked(request):

    return render(request,'accounts/account-locked.html')


def change_password_first_login(request,pk):
    '''
    Function called when user first logs on
    '''
    user = User.objects.get(id = pk)
    if request.method == "POST":
       
        user = User.objects.get(id = pk)
        check_old_password = check_password(request.POST['old_password'], user.password)
        if check_old_password:
            if request.POST['old_password'] == request.POST['password1']:                
                messages.warning(request,"The new passwords cannot be the same as the old password")
            else:
                if request.POST['password1'] == request.POST['password2']:
                    try:
                        valid,message = password_validator(request.POST['password1'])
                        if valid:
                            user.set_password(request.POST['password1'])
                            user.save()
                            messages.success(request,"Successfully updated your password, please login")
                            return redirect('accounts:login_user')
                        else:
                            messages.warning(request,message)
                    except Exception as e:
                        messages.warning(request,str(e))
                else:
                    messages.warning(request,"The two new passwords do not match, please make sure they are the same")
        else:
            messages.warning(request,"The old password supplied does not match, please make sure to input a correct password")
   
    return render(request,"accounts/change_password.html",{'user':user})


@login_required()
def reset_password_staff(request,pk):
    #num_gen = number_gen(4)
    password = "AHC1234"

    password_change_date = datetime.now() - timedelta(days=43, hours=-5)

    staff = Staff.objects.get(id = pk)
    if staff.user:
        staff.user.set_password(password)
        user = staff.user
        user.password_change_date = password_change_date
        user.save()
    else:
        user = User.objects.create_user(
            first_name = staff.first_name,
            last_name = staff.last_name,
            email = staff.email.lower(),
            password = password,
            password_change_date = password_change_date,
        )
        user.save()
    try:    
        response = send_email_activation_external(user.email,user.first_name,password) 
    except Exception as e:
        print(str(e),password)  

    return redirect('college:staff_list')  



def reset_password_external(user):
    password = password_gen(14)

    password_change_date = datetime.now() - timedelta(days=25, hours=-5)
    if user:
        user.set_password(password)
        user.password_change_date = password_change_date
        user.save()
        try:    
            response = send_email_rest_password(user.email,user.first_name,password) 
        except Exception as e:
            print(str(e),password)  


@login_required()
def ajax_change_password(request):
    
    if request.POST['password'] == request.POST['password2']:
        user_instance = request.user
        if not user_instance.check_password(request.POST['password']):
            valid_pass, message_password = password_validator(request.POST['password'])

            if valid_pass:
        
                user_instance.set_password(request.POST['password'])
                user_instance.password_change_date = date.today()
                user_instance.save()
                messages.success(request,"Successfully updated your password")
                
                return render(request,'messages.html')
            else:
                messages.warning(request,'The password supplied does not meet the security requirements of the LMS')
                messages.warning(request,message_password)
                return render(request,'messages.html')
        else:
            messages.warning(request,'Sorry the new password cannot be the same as your previous password. Please try again')
            return render(request,'messages.html') 
    else:
        messages.warning(request,"Your passwords do not match, please try again")
        return render(request,'messages.html')
    

def forgot_password(request):    

    if request.method == "POST":
        check_user = User.objects.filter(email__iexact = request.POST['username'])
        if check_user.exists():
            user =  check_user.first()
            token = get_random_string(length=32)
            fp = UserForgetPasswordToken(user = user,token=token)
            fp.save()

            to = [user.email]
            name = user.first_name

            resp = send_email_forgot_password(to,name,token,user.id)

            if resp == 1:
                messages.success(request,"An email has been sent to your email with a link to reset your password")
            else:
                messages.warning(request,"An error has occurred, email was not sent,please contact an administrator to reset your password manually or try again")

            return render(request,'messages.html')
        else:
            messages.warning(request,"It appears you do not have an account on LMS please register")
            return render(request,'messages.html')
        
    if not request.META.get('HTTP_HX_REQUEST'):
        return render(request,'accounts/forgot_password.html')


def select_new_password(request):

    today = date.today()
    token = request.GET['t']
    user_id = request.GET['u']

    fp = UserForgetPasswordToken.objects.filter(user_id=user_id,token=token,created_at__startswith = today,done='No')
    if fp.exists():
        token = fp.first()
        return render(request,'accounts/select_new_password.html',{'user_id':user_id,'token_id':token.id})
    else:
        messages.warning(request,'Unfortunately this forget password link has expired. If you would like to reset your password, please complete the form below')
        return redirect('accounts:forgot_password')


def selected_new_password(request,user_id,token_id):

    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            user_instance = User.objects.get(id=user_id)
            if not user_instance.check_password(request.POST['password1']):
                valid_pass, message_password = password_validator(request.POST['password1'])

                if valid_pass:
            
                    user_instance.set_password(request.POST['password1'])
                    user_instance.password_change_date = date.today()
                    user_instance.save()
                    messages.success(request,"Successfully updated your password")
                    fp = UserForgetPasswordToken.objects.get(id = token_id)
                    fp.done = 'Yes'
                    fp.save()
                    return HttpResponse('<div><meta http-equiv="refresh" content="0; url=/accounts/login/user"></div>')
                else:
                    messages.warning(request,'The password supplied does not meet the security requirements of the LMS')
                    messages.warning(request,message_password)
                    return render(request,'messages.html')
            else:
                messages.warning(request,'Sorry the new password cannot be the same as your previous password. Please try again')
                return render(request,'messages.html') 
        else:
            messages.warning(request,"Your passwords do not match, please try again")
            return render(request,'messages.html')
        


def create_user_profile_external(external_user,role_id,password):
    '''
    function to create user for external role
    '''

    success = False

    password_change_date = datetime.now() - timedelta(days=25, hours=-5)
    
    if external_user.user:
        user = external_user.user
        if user.is_active == 0:
            user.is_active = 1
        user.save()
        success = True
        message = f"You have been successfully onboarded onto the AHC SIMS Platform, please log in using your email address {external_user.email} as your username and the password: {password}"          
                
    else:
        role = Role.objects.get(id = role_id)
        check_user = User.objects.filter(email=external_user.email.lower())
        if check_user.exists():
            user = check_user.first()
            user.roles.add(role)
            msg_register = "A new role has been added to your account, please use your email address and ORIGINAL password to log on. If you do not remember it, click the Forgot Password Button"
            external_user.user = user
            external_user.save()
            BackgroundThreadSendEmail(f'{external_user.first_name} {external_user.last_name}',external_user.email,msg_register,"AHC SIMS Onboarding").start()
            success = True
            message = "A new role has been added to your account, please use your email address and ORIGINAL password to log on. If you do not remember it, click the Forgot Password Button"
        else:
            
            data = {'first_name':external_user.first_name,'last_name':external_user.last_name,'email':external_user.email}
            form = UserForm(data=data)       
            if form.is_valid():
                user = form.save(commit=False)
                user.email = external_user.email.lower()
                user.is_superuser = 0
                user.is_staff = 0
                user.is_active = 1            
                user.set_password(password)
                user.password_change_date = password_change_date
                user.save()
                user.roles.add(role)
                msg_register = f"You have been successfully added onto the AHC SIMS Platform, please log in using your email address {external_user.email} as your username and the password: {password}"          
                external_user.user = user
                external_user.save()
                BackgroundThreadSendEmail(f'{external_user.first_name} {external_user.last_name}',external_user.email,msg_register,"AHC SIMS Onboarding").start()
                success = True
                message = msg_register
            else:
                message = form.errors

    return success,message

    

def activateSDPs(request,application):

    '''
    Check if the applicant is a main contact, if he is, add him to the training provider contact list and create a profile
    '''
    training_provider = application.training_provider
    '''tpf = application.training_provider_tpf.tpf
    

    check_contact_person = TrainingProviderContactPerson.objects.filter(email=tpf.email)

    if not check_contact_person.exists():
        if application.training_provider_tpf.tpf_main_contact == "Yes":
            data = {
                'first_name':tpf.first_name,
                'last_name':tpf.last_name,
                'email':tpf.email,
                'cellphone':tpf.cellphone,
                'designation':tpf.designation,
                'status':tpf.status
                }
            form = TrainingProviderContactsTPFForm(data=data)
            if form.is_valid():
                contact = form.save(commit=False)
                contact.main_contact = application.training_provider_tpf.tpf_main_contact
                contact.training_provider = training_provider
                contact.save()'''

    for contact in training_provider.contacts.filter(main_contact = 'Yes'):
        if not contact.user:
            role = Role.objects.get(id = 29)
            password = password_gen(14)
            check_user = User.objects.filter(email=contact.email.lower())
            if check_user.exists():
                user = check_user.first()
                user.roles.add(role)
                msg_register = "A new role has been added to your account, please use your email address and ORIGINAL password to log on. If you do not remember it, click the Forgot Password Button"
                contact.user = user
                contact.save()
                BackgroundThreadSendEmail(f'{contact.first_name} {contact.last_name}',contact.email,msg_register,"LMS Profile").start()
            else:
                data = {'first_name':contact.first_name,'last_name':contact.last_name,'email':contact.email}
                form = UserForm(data=data)       
                if form.is_valid():
                    user = form.save(commit=False)
                    user.email = contact.email.lower()
                    user.is_superuser = 0
                    user.is_staff = 0
                    user.is_active = 1            
                    user.set_password(password)
                    user.save()
                    user.roles.add(role)
                    msg_register = f"You have beed successfully added onto the LMS Platform, please log in using your email address {contact.email} as your username and the password: {password}"          
                    BackgroundThreadSendEmail(f'{contact.first_name} {contact.last_name}',contact.email,msg_register,"LMS Profile").start()
                else:
                    messages.warning(request,form.errors)


@login_required()
def activate_secondary_sdf(request,pk,secondary_sdf_pk):
    '''
    Activate or deactivate secondary sdf
    '''

    if request.user.logged_in_role_id == 3 or request.user.logged_in_role_id == 4 or request.user.logged_in_role_id == 5:
        secondary_sdf = CompanySecondarySDF.objects.get(id = secondary_sdf_pk)
        if secondary_sdf.user:
            user = secondary_sdf.user
            if user.is_active == 0:
                user.is_active = 1
                secondary_sdf.status = 'Yes'
                secondary_sdf.save()
            else:
                user.is_active = 0
                secondary_sdf.status = 'No'
                secondary_sdf.save()
            user.save()
        else:
            role = Role.objects.get(id = 30)
            check_user = User.objects.filter(email=secondary_sdf.email.lower())
            if check_user.exists():
                user = check_user.first()
                user.roles.add(role)
                msg_register = "A new role (secondary sdf) has been added to your account, please use your email address and ORIGINAL password to log on. If you do not remember it, click the Forgot Password Button"
                secondary_sdf.user = user
                secondary_sdf.status = 'Yes'
                secondary_sdf.save()
                BackgroundThreadSendEmail(f'{secondary_sdf.first_name} {secondary_sdf.last_name}',secondary_sdf.email,msg_register,"LMS Profile").start()
            else:
                password = password_gen(14)
                data = {'first_name':secondary_sdf.first_name,'last_name':secondary_sdf.last_name,'email':secondary_sdf.email.lower()}
                form = UserForm(data=data)       
                if form.is_valid():
                    user = form.save(commit=False)
                    user.email = secondary_sdf.email.lower()
                    user.is_superuser = 0
                    user.is_staff = 0
                    user.is_active = 1            
                    user.set_password(password)
                    user.save()
                    user.roles.add(role)
                    msg_register = f"You have beed successfully added onto the LMS Platform, please log in using your email address {secondary_sdf.email} as your username and the password: {password}"          
                    secondary_sdf.user = user
                    secondary_sdf.status = 'Yes'
                    secondary_sdf.save()
                    BackgroundThreadSendEmail(f'{secondary_sdf.first_name} {secondary_sdf.last_name}',secondary_sdf.email,msg_register,"LMS Profile").start()
                else:
                    messages.warning(request,form.errors)
                    
        return redirect('ssp:view_sdf_application',pk=pk)

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')
    

@login_required()
def board_member_activation(request,pk,activation):
    '''
    board member activation
    '''

    if request.user.logged_in_role_id == 2:
        board_member = BoardMember.objects.get(id = pk)
        if activation == 1:
            #check if user profile exists
            if board_member.user:
                user = board_member.user
                user.is_active = 1
                user.save()
                board_member.active = 'Yes'
                board_member.save()
            else:
                role = Role.objects.get(id = 39)
                check_user = User.objects.filter(email=board_member.email.lower())
                if check_user.exists():
                    user = check_user.first()
                    user.roles.add(role)
                    msg_register = "A new role (Board Member) has been added to your account, please use your email address and ORIGINAL password to log on. If you do not remember it, click the Forgot Password Button"
                    board_member.user = user
                    board_member.active = 'Yes'
                    board_member.save()
                    BackgroundThreadSendEmail(f'{board_member.first_name} {board_member.last_name}',board_member.email,msg_register,"LMS Profile").start()
                else:
                    password = password_gen(14)
                    data = {'first_name':board_member.first_name,'last_name':board_member.last_name}
                    form = UserForm(data=data)       
                    if form.is_valid():
                        user = form.save(commit=False)
                        user.email = board_member.email.lower()
                        user.is_superuser = 0
                        user.is_staff = 0
                        user.is_active = 1            
                        user.set_password(password)
                        user.save()
                        user.roles.add(role)
                        msg_register = f"You have beed successfully added onto the LMS Platform, please log in using your email address {board_member.email} as your username and the password: {password}"          
                        board_member.user = user
                        board_member.active = 'Yes'
                        board_member.save()
                        BackgroundThreadSendEmail(f'{board_member.first_name} {board_member.last_name}',board_member.email,msg_register,"LMS Profile").start()
                    else:
                        messages.warning(request,form.errors)

                messages.success(request,'Successfully created account and activated board member')

        else:
            if board_member.user:
                user = board_member.user
                if user.roles.count() == 1:
                    user.is_active = 0
                    user.save()

            board_member.active = 'No'
            board_member.save()

            messages.success(request,'Successfully deactivated board member')
                    
        return redirect('mict:admin_board_members')

    else:
        messages.warning(request,"You do not have rights to that portion of the site, you have been logged off!")
        return redirect('accounts:logout')

