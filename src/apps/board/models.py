from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.core.models import BaseModel


class BoardQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)

    def all_boards(self):
        return self.all()


class BoardModel(BaseModel):
    title = models.CharField(_('Title'), max_length=128)
    description = models.TextField(_('Description'), blank=True, null=True)
    is_archived = models.BooleanField(_('Is Archived'), default=False, blank=True, null=True)
    team = models.ForeignKey('team.TeamModel', verbose_name=_('Team'), on_delete=models.CASCADE, related_name='boards')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Created by'), on_delete=models.SET_NULL, null=True, related_name='created_boards')

    objects = BoardQuerySet.as_manager()

    class Meta:
        unique_together = ('title', 'team')
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")

    def archive_board(self):
        if not self.is_archived:
            self.is_archived = True
            self.save()

    def restore_board(self):
        if self.is_archived:
            self.is_archived = False
            self.save()

