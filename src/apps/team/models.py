from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from .enums import JoinTeamStatusEnum


class TeamModel(BaseModel):

    name = models.CharField(_('Team name'), max_length=128)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Created by'), null=True, on_delete=models.SET_NULL, related_name='created_teams')
    description = models.TextField(_('Description'), blank=True, null=True)
    is_public = models.BooleanField(_('Is public'), default=False)
    is_locked = models.BooleanField(_('Is locked'), default=False)

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

    def __str__(self):
        return self.name

    def member_count(self):
        return self.membership.count()

    def is_team_public(self):
        return _('Public') if self.is_public else _('Private')

    def lock_team(self):
        self.is_locked = True
        self.save()

    def change_team_visibility(self, is_public):
        self.is_public = is_public
        self.save()


class TeamMembership(BaseModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey(TeamModel, verbose_name=_('Team'), on_delete=models.CASCADE, related_name='membership')
    responsible = models.CharField(_('Responsible'), max_length=120)

    class Meta:
        unique_together = ('user', 'team')
        verbose_name = _("TeamMemberShip")
        verbose_name_plural = _("TeamMemberShips")

    def __str__(self):
        return f'{self.user.full_name()} - {self.team.name}'

    @classmethod
    def is_member(cls, user, team):
        return cls.objects.filter(user=user, team=team).exists()


class TeamInvitation(BaseModel):
    STATUS_CHOICES = JoinTeamStatusEnum

    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Inviter'), on_delete=models.CASCADE, related_name='sent_team_invitations')
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Invitee'), on_delete=models.CASCADE, related_name='received_team_invitations')
    team = models.ForeignKey(TeamModel, verbose_name=_('Team'), on_delete=models.CASCADE)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES.PENDING)

    class Meta:
        unique_together = ('invitee', 'team')
        verbose_name = _("TeamInvitation")
        verbose_name_plural = _("TeamInvitations")

    def __str__(self):
        return f"Invitation from {self.inviter.full_name()} > {self.invitee.full_name()}"


class TeamJoinRequest(models.Model):
    STATUS_CHOICES = JoinTeamStatusEnum

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.CASCADE, related_name='team_join_requests')
    team = models.ForeignKey(TeamModel, verbose_name=_('Team'), on_delete=models.CASCADE, related_name='join_requests')
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Resolved_by'), null=True, blank=True, on_delete=models.SET_NULL, related_name='resolved_join_requests')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES.PENDING)

    class Meta:
        unique_together = ('user', 'team')
        verbose_name = _("TeamJoinRequest")
        verbose_name_plural = _("TeamJoinRequests")

    def __str__(self):
        return f'{self.team.name} - {self.status}'






