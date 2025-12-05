import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def event_sendgrid_email():
    message = Mail(
    from_email='info@wilms.co.za',
    to_emails='mark@wilms.co.za',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
