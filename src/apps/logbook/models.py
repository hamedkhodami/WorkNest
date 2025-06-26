from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.team.models import TeamModel
from apps.board.models import BoardModel
from .enums import LogEventEnum


class LogEntryModel(BaseModel):
    event = models.CharField(_('Event'), max_length=32, choices=LogEventEnum.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name="activity_logs", verbose_name=_('Actor')
    )
    team = models.ForeignKey(
        TeamModel, null=True, on_delete=models.CASCADE,
        related_name="activity_logs", verbose_name=_('Team')
    )
    board = models.ForeignKey(
        BoardModel, null=True, blank=True, on_delete=models.CASCADE,
        related_name="activity_logs", verbose_name=_('Board')
    )
    target_id = models.UUIDField()
    target_repr = models.CharField(max_length=255)
    extra_data = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = _("Log Entry")
        verbose_name_plural = _("Log Entries")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_event_display()} by {self.actor or 'system'} @ {self.created_at:%Y-%m-%d %H:%M}"
