# test/factories.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from ..models import UserProfileModel, UserBlock
from ..enums import UserRoleEnum, UserGenderEnum

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    phone_number = factory.Sequence(lambda n: f'+9891234567{n:02}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = UserRoleEnum.VIEWER
    first_name = 'تست'
    last_name = 'کاربر'
    national_id = factory.Sequence(lambda n: f'12345678{n:03}')


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfileModel

    user = factory.SubFactory(UserFactory)
    gender = UserGenderEnum.MALE
    bio = 'توضیحات تستی'
    degree = 'کارشناسی'
    city = 'تهران'
    skills = 'Python, Django'


class UserBlockFactory(DjangoModelFactory):
    class Meta:
        model = UserBlock

    user = factory.SubFactory(UserFactory)
    admin = factory.SubFactory(UserFactory)
    note = 'کاربر مسدود شده توسط ادمین'