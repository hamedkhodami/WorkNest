from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LogbookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.logbook'
    verbose_name = _('LogBook')

    def ready(self):
        from . import signals
