import pytest
import json
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from config.asgi import application
from apps.chat.models import ChatRoomModel
from apps.account.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_chat_consumer_send_and_receive():
    user = await database_sync_to_async(UserFactory)()

    room = await database_sync_to_async(ChatRoomModel.objects.create)()
    await database_sync_to_async(room.participants.add)(user)

    communicator = WebsocketCommunicator(
        application=application,
        path=f"/ws/chat/{room.id}/"
    )
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected is True

    test_message = "سلام دنیا"
    await communicator.send_json_to({"message": test_message})

    response = await communicator.receive_json_from()
    assert response["message"] == test_message
    assert response["sender"] == user.full_name()

    await communicator.disconnect()