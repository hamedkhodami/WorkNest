from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class NotificationType(TextChoices):
    EMAIL = 'EMAIL', _('Email')
    SMS = 'SMS', _('SMS')
    IN_APP = 'IN_APP', _('In-app')


class NotificationStatus(TextChoices):
    PENDING = 'PENDING', _('Pending')
    SENT = 'SENT', _('Sent')
    FAILED = 'FAILED', _('Failed')
