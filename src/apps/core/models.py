import uuid

from django.utils.functional import LazyObject
from django.db import models
from django.contrib.auth import get_user_model

from .utils import get_timesince_persian


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        self._is_created = False
        if self._state.adding:
            self._is_created = True
        super().save(*args, **kwargs)
        if self._is_created:
            self.do_create(*args, **kwargs)
        self.do_save(*args, **kwargs)

    def do_save(self, *args, **kwargs):
        pass

    def do_create(self, *args, **kwargs):
        pass

    def get_created_at(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def get_created_at_timepast(self):
        return get_timesince_persian(self.created_at)

    def get_updated_at(self):
        return self.updated_at.strftime('%Y-%m-%d %H:%M:%S')

    def get_updated_at_timepast(self):
        return get_timesince_persian(self.updated_at)


class UserModelLazy(LazyObject):

    def _setup(self):
        self._wrapped = get_user_model()