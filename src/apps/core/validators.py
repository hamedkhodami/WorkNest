import re

from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError


@deconstructible
class OnlyPersianCharsValidator:
    message = _('Ensure character are persian')
    code = 'only_persian_chars'

    def __call__(self, value):
        if not bool(re.search(r'[آ-ی]', value)):
            raise ValidationError(self.message, code=self.code)

