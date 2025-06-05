# TODO: After implementing the invitation or join request approval view,
# check here if status == ACCEPTED,
# and then create a new TeamMembership instance for the user


from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver

from apps.account.service.role_manager import update_user_role

from .models import TeamModel, TeamMembership


@receiver(post_save, sender=TeamMembership)
@receiver(post_delete, sender=TeamMembership)
def update_user_role_on_membership_change(sender, instance, **kwargs):
    update_user_role(instance.user)


@receiver(post_delete, sender=TeamModel)
def update_user_role_on_team_delete(sender, instance, **kwargs):
    update_user_role(instance.created_by)



