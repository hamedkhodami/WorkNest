import json
import requests

from django.core.mail import send_mail as _send_email_django
from django.conf import settings
from django_q.tasks import async_task, Schedule

from apps.core.models import UserModelLazy

User = UserModelLazy


def send_sms(phone_number, pattern_code, values=None):
    if not values:
        values = {}
    phone_number = str(phone_number).replace('+', '')
    payload = json.dumps({
        "pattern_code": pattern_code,
        "originator": settings.SMS_CONFIG['ORIGINATOR'],
        "recipient": phone_number,
        "values": values
    })
    headers = {
        'Authorization': "AccessKey {}".format(settings.SMS_CONFIG['API_KEY']),
        'Content-Type': 'application/json'
    }

    async_task(requests.request,
               'POST',
               settings.SMS_CONFIG['API_URL'],
               headers=headers,
               data=payload
               )


def send_email(email, subject, content, **kwargs):
    # send email in background
    async_task(_send_email_django,
               subject,
               content,
               settings.EMAIL_HOST_USER,
               [email]
               )
