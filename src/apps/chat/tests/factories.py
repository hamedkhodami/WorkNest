import factory
from apps.chat.models import ChatRoomModel, MessageModel
from apps.account.tests.factories import UserFactory


class ChatRoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatRoomModel

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.participants.add(user)
        else:
            self.participants.add(UserFactory(), UserFactory())


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MessageModel

    room = factory.SubFactory(ChatRoomFactory)
    sender = factory.LazyAttribute(lambda o: o.room.participants.first())
    content = factory.Faker("paragraph")
    is_read = False



