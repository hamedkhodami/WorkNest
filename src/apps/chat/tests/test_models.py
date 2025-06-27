import pytest
from apps.chat.tests.factories import ChatRoomFactory, MessageFactory
from apps.account.tests.factories import UserFactory


@pytest.mark.django_db
class TestChatRoomModel:

    def test_chat_room_creation_with_participants(self):
        user1 = UserFactory()
        user2 = UserFactory()

        room = ChatRoomFactory(participants=[user1, user2])

        assert room.participants.count() == 2
        assert user1 in room.participants.all()
        assert user2 in room.participants.all()


@pytest.mark.django_db
class TestMessageModel:

    def test_message_creation_for_room(self):
        user1 = UserFactory()
        user2 = UserFactory()
        room = ChatRoomFactory(participants=[user1, user2])

        message = MessageFactory(room=room, sender=user1)

        assert message.room == room
        assert message.sender == user1
        assert message.content is not None
        assert not message.is_read