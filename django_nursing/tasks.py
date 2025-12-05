from background_task import background
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from students.models import Student,EmailPreferences

def send_sendgrid_email_general(sender_name,sender_email,from_email,to,name,msg,subject,title):

    message = Mail(
    from_email=from_email,
    to_emails=to)

    message.dynamic_template_data = {
    'name': name,
    'message': msg,
    'subject':subject,
    'title':title,
    'sender_name':sender_name,
    'sender_email':sender_email
    }

    message.template_id = 'd-6c1a1245015d47ae9d568523c423abf5'

    try:
        sg = SendGridAPIClient('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')

        response = sg.send(message)

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))


@background(schedule=60)
def notify_user(student_id):
    # lookup user by id and send them a message
    student = Student.objects.get(id=student_id)
    print(student.email)
    send_sendgrid_email_general('Mark','mmuwanguzi@gmail.com','noreply@wilms.co.za','student.email','student.name','testing','testing Subject','testing title')
