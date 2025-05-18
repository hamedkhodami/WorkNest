import secrets
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.db.models.functions import Concat
from django.db.models import Count, Value, Q
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.validators import OnlyPersianCharsValidator
from apps.core.utils import random_num, get_coded_phone_number
from apps.core.models import BaseModel

from .enums import UserRoleEnum,UserGenderEnum
from . import text
from .auth.utils import is_melli_code


class CustomQuerySet(models.QuerySet):

    def search(self, value):
        if not value:
            return self
        qs = self.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
        lookup = Q(phonenumber=value) | Q(full_name__icontains=value)
        return qs.filter(lookup)

    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        if count == 0:
            return None
        return self.order_by('?').first()


class CustomObjectsManager(BaseUserManager):
    _queryset_class = CustomQuerySet

    def create_user(self, phone_number, password, role, email=None, **extra_fields):
        if not phone_number:
            raise ValueError(text.required_phone_number)
        user = self.model(phone_number=phone_number, role=role, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        return self.create_user(phone_number=phone_number, password=password, role='super_user', **extra_fields)

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, userblock__isnull=True)

    @property
    def all_users(self):
        return self.get_queryset()

    @property
    def available_users(self):
        return self.all_users.exclude(role='super_user')

    @property
    def project_admins(self):
        return self.all_users.filter(role='project_admin')

    @property
    def admin(self):
        return self.all_users.filter(role='admin')

    @property
    def members(self):
        return self.all_users.filter(role='project_member')


def generate_referral():
    return secrets.token_hex(4)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):

    Role = UserRoleEnum

    phone_number = PhoneNumberField(region='IR', unique=True, verbose_name=_('Phone number'))
    email = models.EmailField(_('Email'), max_length=225, null=True, blank=True)
    first_name = models.CharField(_('First name'), max_length=128, null=True, blank=True,
                                  default=_('No Name'), validators=[OnlyPersianCharsValidator])
    last_name = models.CharField(_('Last name'), max_length=128, null=True, blank=True,
                                 default=_('No Name'), validators=[OnlyPersianCharsValidator])
    role = models.CharField(_('Role'), max_length=20, choices=Role.choices, default=Role.VIEWER)
    referral_code = models.CharField(default=generate_referral, max_length=8, unique=True)
    national_id = models.CharField(_('National id'),max_length=11, unique=True,
                                   validators=[MaxValueValidator(11),MinValueValidator(9)])

    is_phone_number_confirmed = models.BooleanField(default=False)
    is_national_id_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(_('Active'), default=True)


    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomObjectsManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = '-created_at',

    def __str__(self):
        return f"{self.phone_number} - {self.email or 'No Email'}"

    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or _('No Name')

    @property
    def is_blocked(self):
        try:
            self.userblock
            return True
        except ObjectDoesNotExist:
            return False

    def has_role(self, role_name):
        return self.role == role_name

    @property
    def is_admin_project_user(self):
        return self.has_role('project_admin')

    @property
    def raw_phone_number(self):
        return get_coded_phone_number(self.phone_number)

    def national_id_check(self, phone_number, national_id):
        if not is_melli_code(national_id):
            return False

        user = User.objects.filter(phone_number=phone_number, national_id=national_id).first()
        return user is not None

    def national_id_check_by_data(self, phone_number, national_id):
        if not is_melli_code(national_id):
            return False

        if self.phone_number != phone_number or self.national_id != national_id:
            return False

        return True


class UserProfileModel(BaseModel):

    Gender = UserGenderEnum

    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(_('Gender'), max_length=10, choices=Gender.choices, null=True, blank=True)
    bio = models.TextField(_('Bio'), blank=True, null=True)
    image = models.ImageField(_('Picture'), upload_to='images/profiles/', null=True, blank=True)
    degree = models.CharField(_('Degree'), max_length=128, null=True, blank=True)
    city = models.CharField(_('City'), max_length=64, null=True, blank=True)
    skills = models.TextField(_('Skills'), blank=True, null=True)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('Users profile')

    def __str__(self):
        return f'{self.user}'

    def get_profile_picture_url(self):
        if self.image:
            return self.image.url
        return ".../static/images/default/profile.jpg"


class UserBlock(BaseModel):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='blocked_user')
    admin = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='user_blocked_by_admin')
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Blocked User')
        verbose_name_plural = _('Blocked Users')

    def __str__(self):
        return f'{self.user}'

    def is_blocked_by_admin(self, admin_user):
        return self.admin == admin_user

