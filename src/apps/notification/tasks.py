import logging
from ippanel import Client
from celery import shared_task
from django.core.mail import send_mail as django_send_mail


from apps.core.utils import get_coded_phone_number
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(self, subject, recipients, context):
    try:
        body = "\n".join([f"{k}: {v}" for k, v in context.items()])
        django_send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False
        )
        logger.info(f"Email sent to {recipients}")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms(self, phone_number, pattern, data):
    try:

        phone_number = get_coded_phone_number(phone_number).replace('+', '')

        sms = Client(settings.SMS_CONFIG['API_KEY'])

        sms.send_pattern(
            pattern,
            settings.SMS_CONFIG['ORIGINATOR'],
            phone_number,
            data
        )

        logger.info(f"SMS sent to {phone_number} with pattern {pattern}")

    except Exception as e:
        logger.error(f"SMS sending failed for {phone_number}: {e}")
        raise self.retry(exc=e)

