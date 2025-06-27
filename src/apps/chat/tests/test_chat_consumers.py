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
    # ساخت کاربر
    user = await database_sync_to_async(UserFactory)()

    # ساخت روم و اضافه کردن کاربر
    room = await database_sync_to_async(ChatRoomModel.objects.create)()
    await database_sync_to_async(room.participants.add)(user)

    # ساخت WebSocketCommunicator با user authenticated
    communicator = WebsocketCommunicator(
        application=application,
        path=f"/ws/chat/{room.id}/"
    )
    # قرار دادن user داخل scope (برای AuthMiddleware)
    communicator.scope["user"] = user

    # اتصال موفق
    connected, _ = await communicator.connect()
    assert connected is True

    # ارسال پیام
    test_message = "سلام دنیا"
    await communicator.send_json_to({"message": test_message})

    # دریافت پیام در خروجی
    response = await communicator.receive_json_from()
    assert response["message"] == test_message
    assert response["sender"] == user.full_name()

    # قطع اتصال
    await communicator.disconnect()