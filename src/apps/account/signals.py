from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfileModel



# User model save receiver (Create profile)
@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, *args, **kwargs):
    if created:
        UserProfileModel.objects.create(user=instance)