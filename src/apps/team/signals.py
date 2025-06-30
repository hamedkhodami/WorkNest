from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .service.role_manager import update_user_role
from . import enums, models


@receiver(post_save, sender=models.TeamJoinRequest)
def create_membership_if_accepted(sender, instance, **kwargs):
    """ Creates a TeamMembership if join request is accepted """
    if instance.status == enums.JoinTeamStatusEnum.ACCEPTED:
        models.TeamMembership.objects.get_or_create(
            user=instance.user,
            team=instance.team,
            responsible="Member"
        )


@receiver(post_save, sender=models.TeamMembership)
@receiver(post_delete, sender=models.TeamMembership)
def update_user_role_on_membership_change(sender, instance, **kwargs):
    update_user_role(instance.user)


@receiver(post_delete, sender=models.TeamModel)
def update_user_role_on_team_delete(sender, instance, **kwargs):
    update_user_role(instance.created_by)



