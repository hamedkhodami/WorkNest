from apps.account.models import User
from .models import Notification
from .enums import NotificationType, NotificationStatus


def create_notify_admins(n_type, title, description=None, kwargs=None, **kw):
    """
    Create a notification for all admins (super_user or operator_user).
    """
    admins = User.base_objects.filter(role__in=['super_user', 'operator_user'])
    notifications = []
    for admin in admins:
        notif = Notification(
            type=n_type,
            title=title,
            description=description,
            kwargs=kwargs,
            user=admin,
            email=admin.email,
            phone_number=admin.phone_number,
            **kw
        )
        notif.save()
        notifications.append(notif)
    return notifications


def create_notify(n_type, user, title, description=None, kwargs=None, **kw):
    """
    Create a notification for a specific user.
    """
    return Notification.objects.create(
        type=n_type,
        title=title,
        description=description,
        kwargs=kwargs,
        user=user,
        email=user.email,
        phone_number=user.phone_number,
        **kw
    )

