import factory
from factory.django import DjangoModelFactory

from apps.logbook.models import LogEntryModel
from apps.logbook.enums import LogEventEnum
from apps.account.tests.factories import UserFactory
from apps.team.tests.factories import TeamFactory
from apps.board.tests.factories import BoardFactory


class LogEntryFactory(DjangoModelFactory):
    class Meta:
        model = LogEntryModel

    event = factory.Iterator([e[0] for e in LogEventEnum.choices])
    actor = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)
    board = factory.SubFactory(BoardFactory)
    target_id = factory.Faker('uuid4')
    target_repr = factory.Faker('sentence', nb_words=6)
    extra_data = factory.LazyFunction(lambda: {"ip": "127.0.0.1", "user_agent": "test-browser"})
