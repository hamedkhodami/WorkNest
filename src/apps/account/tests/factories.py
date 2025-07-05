import factory
from apps.account.models import User, UserProfileModel, UserBlock
from apps.account.enums import UserRoleEnum, UserGenderEnum


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    phone_number = factory.Sequence(lambda n: f"+9891234567{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    national_id = factory.Sequence(lambda n: f"{n:010d}")
    role = UserRoleEnum.VIEWER
    is_active = True
    is_superuser = False
    is_staff = False
    password = factory.PostGenerationMethodCall("set_password", "testpassword123")

    class Params:
        admin = factory.Trait(role=UserRoleEnum.ADMIN, is_superuser=True, is_staff=True)
        project_admin = factory.Trait(role=UserRoleEnum.PROJECT_ADMIN, is_superuser=False, is_staff=True)
        project_member = factory.Trait(role=UserRoleEnum.PROJECT_MEMBER, is_superuser=False, is_staff=False)
        viewer = factory.Trait(role=UserRoleEnum.VIEWER, is_superuser=False, is_staff=False)
        team_user = factory.Trait(
            role=factory.Iterator([UserRoleEnum.ADMIN, UserRoleEnum.PROJECT_ADMIN, UserRoleEnum.PROJECT_MEMBER]))


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfileModel

    user = factory.SubFactory(UserFactory)
    gender = factory.Iterator(UserGenderEnum.values)
    bio = factory.Faker("text", max_nb_chars=200)
    image = None
    degree = factory.Faker("job")
    city = factory.Faker("city")
    skills = factory.Faker("sentence", nb_words=6)


class UserBlockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserBlock

    user = factory.SubFactory(UserFactory)
    admin = factory.SubFactory(UserFactory, role=UserRoleEnum.ADMIN)
    note = factory.Faker("sentence", nb_words=10)
