from apps.team import models, enums
from django.utils.translation import gettext_lazy as _
STATUS_CHOICES = enums.JoinTeamStatusEnum


def create_membership_if_accepted(join_request):
    """Creates membership if request is accepted"""
    if join_request.status == STATUS_CHOICES.ACCEPTED:
        models.TeamMembership.objects.create(
            user=join_request.user,
            team=join_request.team,
            responsible=_("Member")
        )
