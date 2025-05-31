from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class JoinTeamStatusEnum(TextChoices):
    PENDING = 'pending', _('Pending')
    ACCEPTED = 'accepted', _('Accepted')
    REJECTED = 'rejected', _('Rejected')

