from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from jsonfield import JSONField

from apps.core.models import BaseModel
from .enums import NotificationType, NotificationStatus


class Notification(BaseModel):
    type = models.CharField(_('Notification Type'), max_length=20, choices=NotificationType.choices)
    status = models.CharField(_('Status'), max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)

    title = models.CharField(_('Title'), max_length=150)
    description = models.TextField(_('Description'), blank=True, null=True)
    kwargs = JSONField(_('Extra Data'), blank=True, null=True)

    to_user = models.ForeignKey('account.User', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('User'))
    email = models.EmailField(_('Email'), blank=True, null=True)
    phone_number = PhoneNumberField(_('Phone Number'), region='IR', blank=True, null=True)

    is_visited = models.BooleanField(_('Is Visited'), default=False)
    retry_count = models.PositiveIntegerField(_('Retry Count'), default=0)
    sent_at = models.DateTimeField(_('Sent At'), blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return f"{self.type} notification for {self.to_user or self.email or self.phone_number}"

    def get_title(self):
        return self.title or _('Notification')

    def get_content(self):
        return f"{self.get_title()}\n{self.description or ''}"

    def get_link(self):
        try:
            return self.kwargs.get('link')
        except (AttributeError, TypeError):
            return None

