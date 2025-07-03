from .models import Notification
from .enums import NotificationType


def create_notify(to_user, title, description=None, kwargs=None, n_type=None, **kw):
    """
    Create a notification for a specific user, and auto-detect type if not provided.
    """

    email = to_user.email
    phone_number = to_user.phone_number

    if not n_type:
        if email:
            n_type = NotificationType.EMAIL
        elif phone_number:
            n_type = NotificationType.SMS
        else:
            n_type = NotificationType.IN_APP

    return Notification.objects.create(
        type=n_type,
        title=title,
        description=description,
        kwargs=kwargs,
        to_user=to_user,
        **kw
    )

