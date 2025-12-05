from django.shortcuts import render,redirect
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail, BadHeaderError,send_mass_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import Group
from django.contrib import messages
from datetime import datetime
import threading
import random
import os

def send_email_activation_student(from_email,to,name,password):

    msg_plain = render_to_string('email_templates/student_activation.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/student_activation.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'LMS Account Activation',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_password_reset_student(to,name,password):

    msg_plain = render_to_string('email_templates/student_password_reset.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/student_password_reset.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'LMS Password Reset',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_activation_staff(to,name,password):
    msg_plain = render_to_string('email_templates/staff_activation.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/staff_activation.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'LMS Account Activation',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_reset_password_staff(to,name,password):
    msg_plain = render_to_string('email_templates/staff_password_reset.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/staff_password_reset.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'LMS Password Reset',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,'nursing@elevatelearn.co.za'],
        html_message=msg_html,
    )

    return response

def send_email_registration_company(to,name,from_name,from_email):
    msg_plain = render_to_string('email_templates/company_registration.txt', {'name': name,'repname':from_name,'repemail':from_email})
    msg_html = render_to_string('email_templates/company_registration.html', {'name': name,'repname':from_name,'repemail':from_email})

    response = send_mail(
        'LMS Account Registration',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_registration_alert(name,to,company,contact,email,telephone,cellphone):

    msg_plain = render_to_string('email_templates/staff_company_registration_alert.txt', {'name': name,'company':company,'contact':contact,'email':email,'telephone':telephone,'cellphone':cellphone})
    msg_html = render_to_string('email_templates/staff_company_registration_alert.html', {'name': name,'company':company,'contact':contact,'email':email,'telephone':telephone,'cellphone':cellphone})

    response = send_mail(
        'LMS Company Registration',
        msg_plain,
        'nursing@elevatelearn.co.za',
        to,
        html_message=msg_html,
    )

    return response



def send_email_activation_mentor(to,name,password,from_name,from_email):
    msg_plain = render_to_string('email_templates/company_mentor_activation.txt', {'name': name,'email':to,'password':password,'from_name':from_name,'from_email':from_email})
    msg_html = render_to_string('email_templates/company_mentor_activation.html', {'name': name,'email':to,'password':password,'from_name':from_name,'from_email':from_email})

    response = send_mail(
        'LMS Account Activation',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,from_email],
        html_message=msg_html,
    )

    return response

def send_email_event_registration(to,name,from_name,from_email):

    msg_plain = render_to_string('email_templates/company_event_registration.txt', {'name': name,'from_name':from_name,'from_email':from_email})
    msg_html = render_to_string('email_templates/company_event_registration.html', {'name': name,'from_name':from_name,'from_email':from_email})

    response = send_mail(
        'LMS New Recruitment Program Registration Received',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_event_registration_alert(name,to,company,contact,email,telephone,cellphone):

    msg_plain = render_to_string('email_templates/event_registration_alert.txt', {'name': name,'company':company,'contact':contact,'email':email,'telephone':telephone,'cellphone':cellphone})
    msg_html = render_to_string('email_templates/event_registration_alert.html', {'name': name,'company':company,'contact':contact,'email':email,'telephone':telephone,'cellphone':cellphone})

    response = send_mail(
        'LMS New Recruitment Program Registration',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_advert_notification(to,name,company,contact,position):
    msg_plain = render_to_string('email_templates/staff_advert_alert.txt', {'name': name,'company':company,'contact':contact,'position':position})
    msg_html = render_to_string('email_templates/staff_advert_alert.html', {'name': name,'company':company,'contact':contact,'position':position})

    response = send_mail(
        'LMS New Job Placement',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response


def send_email_advert_updated_notification(to,name,company,advert_old,advert_new):
    msg_plain = render_to_string('email_templates/staff_advert_updated.txt', {'name':name,'company':company,'position_old':advert_old.position,'position_new':advert_new.position,'description_old':advert_old.description,'description_new':advert_new.description,'type_old':advert_old.type.type,'type_new':advert_new.type.type,'paid_old':advert_old.paid,'paid_new':advert_new.paid,'requirements_old':advert_old.requirements,'requirements_new':advert_new.requirements,'cut_off_date_old':advert_old.cut_off_date,'cut_off_date_new':advert_new.cut_off_date})
    msg_html = render_to_string('email_templates/staff_advert_updated.html', {'name':name,'company':company,'position_old':advert_old.position,'position_new':advert_new.position,'description_old':advert_old.description,'description_new':advert_new.description,'type_old':advert_old.type.type,'type_new':advert_new.type.type,'paid_old':advert_old.paid,'paid_new':advert_new.paid,'requirements_old':advert_old.requirements,'requirements_new':advert_new.requirements,'cut_off_date_old':advert_old.cut_off_date,'cut_off_date_new':advert_new.cut_off_date})

    response = send_mail(
        'LMS Job Placement Update',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response


def send_email_advert_apporved(from_name,to,name,position,from_email):
    msg_plain = render_to_string('email_templates/company_advert_approved.txt', {'name': name,'from_email':from_email,'from_name':from_name,'position':position})
    msg_html = render_to_string('email_templates/company_advert_approved.html', {'name': name,'from_email':from_email,'from_name':from_name,'position':position})

    response = send_mail(
        'LMS New Job Placement',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_student_event_message(to,title,name,message,from_email,from_name,subject):
    msg_plain = render_to_string('email_templates/student_event_email.txt', {'name': name,'from_email':from_email,'from_name':from_name,'title':title,'message':message})
    msg_html = render_to_string('email_templates/student_event_email.html', {'name': name,'from_email':from_email,'from_name':from_name,'title':title,'message':message})

    msg = EmailMultiAlternatives(subject, msg_plain, "nursing@elevatelearn.co.za",[from_email],to)
    msg.attach_alternative(msg_html, "text/html")
    response = msg.send()

    return response

def send_email_general_message(to,message,subject,from_email,file=None):
    msg_html = render_to_string('email_templates/general_blank.html', {'message':message})
    msg_plain = render_to_string('email_templates/general_blank.txt', {'message':message})

    msg = EmailMultiAlternatives(subject=subject,body=msg_plain, from_email="nursing@elevatelearn.co.za",to=[from_email],bcc=to,reply_to=[from_email])
    msg.attach_alternative(msg_html, "text/html")
    if file != None:
        msg.attach_file(file)
    response = msg.send()

    return response

def send_email_appointment_update(to,bcc,name,description,category,date,time,update):
    msg_html = render_to_string('email_templates/student_appointment_update.html', {'name':name,'description':description,'category':category,'date':date,'time':time,'update':update})
    msg_plain = render_to_string('email_templates/student_appointment_update.txt', {'name':name,'description':description,'category':category,'date':date,'time':time,'update':update})

    msg = EmailMultiAlternatives(subject="Appointment Update",body=msg_plain, from_email="nursing@elevatelearn.co.za",to=to,bcc=bcc,reply_to=[bcc])
    msg.attach_alternative(msg_html, "text/html")
    response = msg.send()

    return response


def send_email_activation_company(to,name,password,from_name,from_email,bcc):
    msg_plain = render_to_string('email_templates/company_contact_activation.txt', {'name': name,'email':to,'password':password,'from_name':from_name,'from_email':from_email})
    msg_html = render_to_string('email_templates/company_contact_activation.html', {'name': name,'email':to,'password':password,'from_name':from_name,'from_email':from_email})

    msg = EmailMultiAlternatives(subject="LMS Account Activation",body=msg_plain, from_email="nursing@elevatelearn.co.za",to=[to],bcc=bcc,reply_to=[from_email])
    msg.attach_alternative(msg_html, "text/html")
    response = msg.send()

    return response


def send_email_appointment_alert(to,fullname,department,contact,email,category,description,appt_date,appt_time):

    msg_plain = render_to_string('email_templates/staff_student_appointment_alert.txt', {'fullname': fullname,'department':department,'contact':contact,'email':email,'category':category,'description':description,'appt_date':appt_date,'appt_time':appt_time})
    msg_html = render_to_string('email_templates/staff_student_appointment_alert.html', {'fullname': fullname,'department':department,'contact':contact,'email':email,'category':category,'description':description,'appt_date':appt_date,'appt_time':appt_time})

    response = send_mail(
        'LMS Appointment Request',
        msg_plain,
        'nursing@elevatelearn.co.za',
        to,
        html_message=msg_html,
    )

    return response


def send_email_appointment_assigned(to,fullname,department,contact,email,category,description,appt_date,appt_time):

    msg_plain = render_to_string('email_templates/staff_student_appointment_assigned.txt', {'fullname': fullname,'department':department,'contact':contact,'email':email,'category':category,'description':description,'appt_date':appt_date,'appt_time':appt_time})
    msg_html = render_to_string('email_templates/staff_student_appointment_assigned.html', {'fullname': fullname,'department':department,'contact':contact,'email':email,'category':category,'description':description,'appt_date':appt_date,'appt_time':appt_time})

    response = send_mail(
        'LMS Appointment Request',
        msg_plain,
        'nursing@elevatelearn.co.za',
        to,
        html_message=msg_html,
    )

    return response


def send_email_forgot_password(to,name,token,user_id):
    msg_plain = render_to_string('email_templates/user_forget_password.txt', {'name': name,'token':token,'user_id':user_id})
    msg_html = render_to_string('email_templates/user_forget_password.html', {'name': name,'token':token,'user_id':user_id})

    msg = EmailMultiAlternatives("LMS Forget Password Reset", msg_plain, "nursing@elevatelearn.co.za",['nursing@elevatelearn.co.za'],to)
    msg.attach_alternative(msg_html, "text/html")
    response = msg.send()

    return response


def sendgrid_student_advert(to,bcc,company,job_post):

    message_sent = False
    error = ''
    
    message = Mail()
    message.add_to(to)
    message.from_email = From('nursing@elevatelearn.co.za', 'LMS Admin')
    #message.set_from('')
    message.add_bcc(bcc)

    message.dynamic_template_data = {
    'company': company,
    'post': job_post,
    }

    message.template_id = 'd-c12a0e43519e469d917ecd354110e073'

    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        if response.status_code == 202:
            message_sent = True
    
    except Exception as e:
        print(str(e))
        error = e.body
    
    return message_sent,error


def sendgrid_student_advert_reminder(to,bcc,company,job_post,name):
    
    message_sent = False
    error = ''
    
    message = Mail()
    message.add_to(to)
    message.from_email = From('nursing@elevatelearn.co.za', 'LMS Admin')
    #message.set_from('')
    message.add_bcc(bcc)

    message.dynamic_template_data = {
    'company': company,
    'post': job_post,
    'name':name,
    }

    message.template_id = 'd-81377c0d61a8408d832673f81c944664'

    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        if response.status_code == 202:
            message_sent = True
    
    except Exception as e:
        print(str(e))
        error = e.body
    
    return message_sent,error


def spaces_send_email_activation_company(to,name,password,website):
    msg_plain = render_to_string('email_templates/spaces_company_contact_activation.txt', {'name': name,'email':to,'password':password,'website':website})
    msg_html = render_to_string('email_templates/spaces_company_contact_activation.html', {'name': name,'email':to,'password':password,'website':website})

    msg = EmailMultiAlternatives(subject="LMS - SPACES Account Activation",body=msg_plain, from_email="nursing@elevatelearn.co.za",to=[to,"nursing@elevatelearn.co.za","liesls@uj.ac.za"])
    msg.attach_alternative(msg_html, "text/html")
    response = msg.send()

    return response


def send_email_students_advert(to,bcc,company,post):
    msg_html = render_to_string('email_templates/student_advert_email.html', {'company':company,'post':post})
    msg_plain = render_to_string('email_templates/student_advert_email.txt', {'company':company,'post':post})

    msg = EmailMultiAlternatives(subject='New Job Advert Posted',body=msg_plain, from_email="nursing@elevatelearn.co.za",to=[to],bcc=bcc,reply_to=['nursing@elevatelearn.co.za'])
    msg.attach_alternative(msg_html, "text/html")
    
    response = msg.send()

    return response


def sendgrid_student_spaces_reminder(to,msg,title):
    
    message_sent = False
    error = ''
    
    message = Mail(
        from_email=('nursing@elevatelearn.co.za', 'LMS Spaces Admin'),
        to_emails=to,
        subject=title,
        is_multiple=True
    )
  
    message.dynamic_template_data = {
    'message': msg,
    'title': title,
    'name':'Delegate',
    }

    message.template_id = 'd-6c1a1245015d47ae9d568523c423abf5'

    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        if response.status_code == 202:
            message_sent = True
    
    except Exception as e:
        print(str(e))

    print(message_sent)
    
    return message_sent,error







def send_email_activation_external(to,name,password):

    msg_plain = render_to_string('email_templates/external_activation.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/external_activation.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'LMS Account Activation',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response


def send_email_rest_password(to,name,password):

    msg_plain = render_to_string('email_templates/external_password_reset.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/external_password_reset.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'MICT SETA LMS Password Reset',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_general(to,name,title,email_body):

    msg_plain = render_to_string('email_templates/general_email.txt', {'name': name,'title':title,'email_body':email_body})
    msg_html = render_to_string('email_templates/general_email.html', {'name': name,'title':title,'email_body':email_body})

    response = send_mail(
        title,
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,'nursing@elevatelearn.co.za'],
        html_message=msg_html,
    )
    
    return response


def send_email_general_multiple(to,name,title,email_body):

    msg_plain = render_to_string('email_templates/general_email.txt', {'name': name,'title':title,'email_body':email_body})
    msg_html = render_to_string('email_templates/general_email.html', {'name': name,'title':title,'email_body':email_body})

    response = send_mail(
        title,
        msg_plain,
        'nursing@elevatelearn.co.za',
        to,
        html_message=msg_html,
    )

    return response


def send_email_general_signoff(to,name,title,email_body,from_person,from_email,department):

    msg_plain = render_to_string('email_templates/general_email_signoff.txt', {'name': name,'title':title,'email_body':email_body,'from_person':from_person,'from_email':from_email,'department':department})
    msg_html = render_to_string('email_templates/general_email_signoff.html', {'name': name,'title':title,'email_body':email_body,'from_person':from_person,'from_email':from_email,'department':department})

    response = send_mail(
        title,
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,'nursing@elevatelearn.co.za'],
        html_message=msg_html,
    )

    return response


def send_email_sdf_approval(to,name,company,sdl_number):

    msg_plain = render_to_string('email_templates/sdf_approval.txt', {'name': name,'company':company,'sdl_number':sdl_number,})
    msg_html = render_to_string('email_templates/sdf_approval.html', {'name': name,'company':company,'sdl_number':sdl_number,})

    response = send_mail(
        'Approval letter for the Skills Development Facilitator',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,'nursing@elevatelearn.co.za'],
        html_message=msg_html,
    )

    return response


def send_email_wsp_received(to,name,wsp_period,company,sdl_number):

    msg_plain = render_to_string('email_templates/sdf_acknowledgement.txt', {'name': name,'wsp_period':wsp_period,'company':company,'sdl_number':sdl_number})
    msg_html = render_to_string('email_templates/sdf_acknowledgement.html', {'name': name,'wsp_period':wsp_period,'company':company,'sdl_number':sdl_number})

    response = send_mail(
        f'Acknowledgement letter of the {wsp_period} WSP/ATR and PTP/PTR submission',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,'nursing@elevatelearn.co.za'],
        html_message=msg_html,
    )

    return response


def send_email_password_reset_student(to,name,password):

    msg_plain = render_to_string('email_templates/student_password_reset.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/student_password_reset.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'LMS Password Reset',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_activation_staff(to,name,password):
    msg_plain = render_to_string('email_templates/staff_activation.txt', {'name': name,'email':to,'password':password})
    msg_html = render_to_string('email_templates/staff_activation.html', {'name': name,'email':to,'password':password})

    response = send_mail(
        'LMS Account Activation',
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to],
        html_message=msg_html,
    )

    return response

def send_email_forgot_password(to,name,token,user_id):
    msg_plain = render_to_string('email_templates/user_forget_password.txt', {'name': name,'token':token,'user_id':user_id})
    msg_html = render_to_string('email_templates/user_forget_password.html', {'name': name,'token':token,'user_id':user_id})

    msg = EmailMultiAlternatives("LMS Forget Password Reset", msg_plain, "nursing@elevatelearn.co.za",to,['nursing@elevatelearn.co.za'])
    msg.attach_alternative(msg_html, "text/html")
    response = msg.send()

    return response



class BackgroundThreadSendEmailTrainingProvider(threading.Thread):
    
    def __init__(self,training_provider,company,learning_programme_tp):
        self.training_provider = training_provider
        self.company = company
        self.learning_programme_tp = learning_programme_tp

        threading.Thread.__init__(self)

    def run(self):

        email_body = ""
        if self.training_provider.status == "Active":
            email_body = f"{self.company.company_name} has added you as a training provider. Please log onto the LMS to approve the programme and view the students."
            for contact in self.training_provider.contacts.filter(main_contact = 'Yes'):   
                send_email_general(
                    f'{contact.email}',
                    f'{contact.title} {contact.first_name} {contact.last_name}',
                    "Training Provider Request",
                    email_body)

        email_body = f"{self.company.company_name} has added you as a training provider."
            
        send_email_general(
            f'{self.learning_programme_tp.email}',
            f'{self.learning_programme_tp.first_name} {self.learning_programme_tp.last_name}',
            "Training Provider Request",
            email_body)        


class BackgroundThreadSendEmailNonFundedTrainingProvider(threading.Thread):
    
    def __init__(self,training_provider,company,non_funded_programme_tp):
        self.training_provider = training_provider
        self.company = company
        self.non_funded_programme_tp = non_funded_programme_tp

        threading.Thread.__init__(self)

    def run(self):

        email_body = ""
        if self.training_provider.status == "Active":
            email_body = f"{self.company.company_name} has added you as a training provider. Please log onto the LMS to approve the programme and view the students."
            for contact_list in self.training_provider.contacts.filter(main_contact = 'Yes'):   
                contact = self.training_provider.contacts.filter(main_contact = 'Yes').first()
                send_email_general(
                    f'{contact.email}',
                    f'{contact.title} {contact.first_name} {contact.last_name}',
                    "Training Provider Request",
                    email_body)

        email_body = f"{self.company.company_name} has added you as a training provider."
            
        send_email_general(
            f'{self.non_funded_programme_tp.contact_email}',
            f'{self.non_funded_programme_tp.contact_first_name} {self.non_funded_programme_tp.contact_last_name}',
            "Training Provider Request",
            email_body)        
 


class BackgroundThreadSendEmail(threading.Thread):
    
    def __init__(self,name,email,email_body,title):
        threading.Thread.__init__(self)
        self.name = name
        self.email_body = email_body
        self.email = email
        self.title = title
        

    def run(self):  
                   
        send_email_general(
            self.email,
            self.name,
            self.title,
            self.email_body)        
        
def send_email_ssp_bulk_upload(to,name,bulk_upload,accepted,rejected,if_rejected):

    msg_plain = render_to_string('email_templates/ssp_bulk_upload.txt', {'name': name,'bulk_upload':bulk_upload,'accepted':accepted,'rejected':rejected,'if_rejected':if_rejected})
    msg_html = render_to_string('email_templates/ssp_bulk_upload.html', {'name': name,'bulk_upload':bulk_upload,'accepted':accepted,'rejected':rejected,'if_rejected':if_rejected})

    response = send_mail(
        "WSP Bulk Upload Outcome",
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,'nursing@elevatelearn.co.za'],
        html_message=msg_html,
    )

    return response


def send_notification_unit_assessment(to,type_assessment,unit,programme,provider):

    msg_plain = render_to_string('email_templates/programme_assessment.txt', {'type_assessment': type_assessment,'unit':unit,'programme':programme,'provider':provider})
    msg_html = render_to_string('email_templates/programme_assessment.html', {'type_assessment': type_assessment,'unit':unit,'programme':programme,'provider':provider})

    response = send_mail(
        f'Unit Standard ready for {type_assessment}',
        msg_plain,
        'nursing@elevatelearn.co.za',
        to,
        html_message=msg_html,
    )

    return response


def send_general_multi_bcc_email(bcc,to,text_content,subject):

    msg = EmailMessage(subject, text_content, 'nursing@elevatelearn.co.za', to= to, bcc=bcc)
    msg.send()


def send_general_multi_bcc_html_email(bcc,to,text_content,subject):

    msg = EmailMessage(subject, text_content, 'nursing@elevatelearn.co.za', to= to, bcc=bcc)    
    msg.content_subtype = "html"
    msg.send()


def send_email_lpd_intervention_reject(to,title,old_window,new_window):

    msg_plain = render_to_string('email_templates/lpd_loi_intervention_reject.txt', {'old_window':old_window,'new_window':new_window})
    msg_html = render_to_string('email_templates/lpd_loi_intervention_reject.html', {'old_window':old_window,'new_window':new_window})

    response = send_mail(
        title,
        msg_plain,
        'nursing@elevatelearn.co.za',
        [to,'nursing@elevatelearn.co.za'],
        html_message=msg_html,
    )

    return response