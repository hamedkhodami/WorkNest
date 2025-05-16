from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class UserRoleEnum(TextChoices):

    ADMIN = 'admin', _('Admin')
    PROJECT_ADMIN = 'project_admin', _('Project admin')
    PROJECT_MEMBER = 'project_member', _('Project member')
    VIEWER = 'viewer', _('Viewer')


class UserGenderEnum(TextChoices):

    MALE = 'm', _('Male')
    FEMALE = 'f', _('Female')