import factory
from apps.board.models import BoardModel
from apps.team.tests.factories import TeamFactory
from apps.account.tests.factories import UserFactory


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BoardModel

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    is_archived = factory.Faker("boolean")
    team = factory.SubFactory(TeamFactory)
    created_by = factory.SubFactory(UserFactory)