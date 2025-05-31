import factory
from apps.team.models import TeamModel


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamModel

    name = factory.Faker("company")
    description = factory.Faker("paragraph")
    is_public = factory.Faker("boolean")
    is_locked = factory.Faker("boolean")