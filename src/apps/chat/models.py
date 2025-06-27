from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class ChatRoomModel(BaseModel):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_room',
                                          verbose_name=_('Participants'))

    class Meta:
        verbose_name = _('ChatRoom')
        verbose_name_plural = _('ChatRooms')
        ordering = ("-created_at",)


class MessageModel(BaseModel):
    room = models.ForeignKey(ChatRoomModel, related_name='messages', on_delete=models.CASCADE,
                             verbose_name=_('Room'))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender', on_delete=models.CASCADE,
                               verbose_name=_('Sender'))
    content = models.TextField(verbose_name=_('Content'))
    is_read = models.BooleanField(_('Is read'), default=False)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ("-created_at",)
