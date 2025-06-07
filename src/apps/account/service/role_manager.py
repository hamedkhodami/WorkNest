from apps.team.models import TeamModel, TeamMembership
from apps.account.enums import UserRoleEnum as Role


def update_user_role(user):
    if TeamModel.objects.filter(created_by=user).exists():
        user.role = Role.PROJECT_ADMIN
    elif TeamMembership.objects.filter(user=user).exists():
        user.role = Role.PROJECT_MEMBER
    else:
        user.role = Role.VIEWER
    user.save(update_fields=['role'])
