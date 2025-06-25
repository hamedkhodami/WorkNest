from apps.core.models import UserModelLazy

from .models import NotificationUser, NotificationUserPhonenumber

User = UserModelLazy()


def create_notify_admins(n_type, title, description=None, kwargs=None, **kw):
    admins = User.base_objects.filter(role__in=['super_user', 'operator_user'])
    for admin in admins:
        n = NotificationUser(
            type=n_type,
            title=title,
            to_user=admin,
            description=description,
            kwargs=kwargs,
            **kw
        )
        n.save()


def create_notify(n_type, user, title, description=None, kwargs=None, **kw):
    return NotificationUser.objects.create(
        type=n_type,
        title=title,
        to_user=user,
        description=description,
        kwargs=kwargs,
        **kw
    )


def create_notify_phone_number(n_type, phone_number, title, description=None, kwargs=None, **kw):
    return NotificationUserPhonenumber.objects.create(
        type=n_type,
        title=title,
        phonenumber=phone_number,
        description=description,
        kwargs=kwargs,
        **kw
    )
