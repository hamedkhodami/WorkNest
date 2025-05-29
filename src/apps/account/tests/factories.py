import factory
from apps.account.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    phone_number = factory.Sequence(lambda n: f"+9891234567{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    national_id = factory.Sequence(lambda n: f"{n:010d}")
    role = "viewer"