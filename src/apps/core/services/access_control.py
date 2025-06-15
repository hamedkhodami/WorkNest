from rest_framework.exceptions import PermissionDenied
from apps.core import text
from apps.team.models import TeamMembership
from apps.account.enums import UserRoleEnum


def is_team_member(user, team):

    if user.role == UserRoleEnum.ADMIN:
        return True

    if not TeamMembership.objects.filter(user=user, team=team).exists():
        raise PermissionDenied(text.permission_denied)

    return True
