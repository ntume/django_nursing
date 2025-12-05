from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import smtplib
import datetime as dt
import icalendar
import pytz
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage

def sendAppointment(self, subj, description):
  # Timezone to use for our dates - change as needed
  tz = pytz.timezone("Europe/London")
  reminderHours = 1
  startHour = 7
  start = tz.localize(dt.datetime.combine(self.date, dt.time(startHour, 0, 0)))
  cal = icalendar.Calendar()
  cal.add('prodid', '-//My calendar application//example.com//')
  cal.add('version', '2.0')
  cal.add('method', "REQUEST")
  event = icalendar.Event()
  event.add('attendee', self.getEmail())
  event.add('organizer', "me@example.com")
  event.add('status', "confirmed")
  event.add('category', "Event")
  event.add('summary', subj)
  event.add('description', description)
  event.add('location', "Room 101")
  event.add('dtstart', start)
  event.add('dtend', tz.localize(dt.datetime.combine(self.date, dt.time(startHour + 1, 0, 0))))
  event.add('dtstamp', tz.localize(dt.datetime.combine(self.date, dt.time(6, 0, 0))))
  event['uid'] = getUniqueId() # Generate some unique ID
  event.add('priority', 5)
  event.add('sequence', 1)
  event.add('created', tz.localize(dt.datetime.now()))

  alarm = icalendar.Alarm()
  alarm.add("action", "DISPLAY")
  alarm.add('description', "Reminder")
  #alarm.add("trigger", dt.timedelta(hours=-reminderHours))
  # The only way to convince Outlook to do it correctly
  alarm.add("TRIGGER;RELATED=START", "-PT{0}H".format(reminderHours))
  event.add_component(alarm)
  cal.add_component(event)

  msg = MIMEMultipart("alternative")

  msg["Subject"] = subj
  msg["From"] = "{0}@example.com".format(self.creator)
  msg["To"] = self.getEmail()
  msg["Content-class"] = "urn:content-classes:calendarmessage"

  msg.attach(MIMEText.MIMEText(description))

  filename = "invite.ics"
  part = MIMEBase.MIMEBase('text', "calendar", method="REQUEST", name=filename)
  part.set_payload( cal.to_ical() )
  encoders.encode_base64(part)
  part.add_header('Content-Description', filename)
  part.add_header("Content-class", "urn:content-classes:calendarmessage")
  part.add_header("Filename", filename)
  part.add_header("Path", filename)
  msg.attach(part)

  email_event = EmailMessage(
      msg["Subject"],
      msg.as_string(),
      msg["From"],
      to='mmuwanguzi@gmail.com',
      reply_to=sender,
      headers={'Message-ID': 'wilms'},
  )

  email_event.send(fail_silently=False)
