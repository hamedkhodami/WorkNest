import factory
from apps.account.models import User
from apps.account.enums import UserRoleEnum


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

    class Params:
        admin = factory.Trait(role=UserRoleEnum.ADMIN, is_superuser=True, is_staff=True)
        project_admin = factory.Trait(role=UserRoleEnum.PROJECT_ADMIN, is_superuser=False, is_staff=True)
        project_member = factory.Trait(role=UserRoleEnum.PROJECT_MEMBER, is_superuser=False, is_staff=False)
        viewer = factory.Trait(role=UserRoleEnum.VIEWER, is_superuser=False, is_staff=False)


