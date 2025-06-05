import factory
from apps.team.models import TeamModel, TeamMembership, TeamJoinRequest
from apps.account.tests.factories import UserFactory
from apps.team import enums


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


class TeamJoinRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamJoinRequest

    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)
    resolved_by = None
    status = factory.Iterator([enums.JoinTeamStatusEnum.PENDING, enums.JoinTeamStatusEnum.ACCEPTED, enums.JoinTeamStatusEnum.REJECTED])