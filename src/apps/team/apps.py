from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TeamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.team'
    verbose_name = _('Team')

    def ready(self):
        from . import signals
