import factory
from apps.team.models import TeamModel, TeamMembership
from apps.account.tests.factories import UserFactory


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamModel

    name = factory.Faker("company")
    description = factory.Faker("paragraph")
    is_locked = factory.Faker("boolean")


class TeamMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamMembership

    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)
    responsible = factory.Faker("job")