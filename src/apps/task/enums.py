from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class TaskPriorityEnum(TextChoices):
    LOW = 'low', _('Low')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('High')
    CRITICAL = 'critical', _('Critical')
