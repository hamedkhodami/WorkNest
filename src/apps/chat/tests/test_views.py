import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from apps.account.tests.factories import UserFactory
from apps.chat.models import ChatRoomModel, MessageModel


@pytest.mark.django_db
class TestChatRoomCreateView:

    def test_create_chat_room_success(self):
        user1 = UserFactory()
        user2 = UserFactory()

        client = APIClient()
        client.force_authenticate(user=user1)

        url = reverse("apps.chat:chatroom-create")
        payload = {
            "participants": [user1.id, user2.id]
        }

        response = client.post(url, payload, format="json")

        assert response.status_code == 201
        data = response.data
        assert "id" in data
        assert len(data["participants"]) == 2

        rooms = ChatRoomModel.objects.filter(participants=user1).filter(participants=user2)
        assert rooms.count() == 1

    def test_create_chat_room_invalid_participant_count(self):
        user1 = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user1)

        url = reverse("apps.chat:chatroom-create")
        payload = {
            "participants": [user1.id]  # فقط یک نفر
        }

        response = client.post(url, payload, format="json")

        assert response.status_code == 400
        assert "participants" in response.data["error"]

    def test_create_chat_room_returns_existing_if_duplicate(self):
        user1 = UserFactory()
        user2 = UserFactory()
        room = ChatRoomModel.objects.create()
        room.participants.set([user1, user2])

        client = APIClient()
        client.force_authenticate(user=user1)

        url = reverse("apps.chat:chatroom-create")
        payload = {
            "participants": [user1.id, user2.id]
        }

        response = client.post(url, payload, format="json")

        assert response.status_code == 201
        rooms = ChatRoomModel.objects.filter(participants=user1).filter(participants=user2)
        assert rooms.count() == 1


@pytest.mark.django_db
class TestUnreadRoomListView:
    def test_unread_room_list_view_returns_correct_rooms(self):
        user = UserFactory()
        opponent = UserFactory()
        other_user = UserFactory()

        # ساخت Room بین user و opponent
        room1 = ChatRoomModel.objects.create()
        room1.participants.set([user, opponent])

        # ساخت پیام‌خوانده‌نشده از طرف opponent
        MessageModel.objects.create(room=room1, sender=opponent, content="سلام", is_read=False)

        # ساخت Room دیگه‌ای که پیام نخونده نداره
        room2 = ChatRoomModel.objects.create()
        room2.participants.set([user, other_user])
        MessageModel.objects.create(room=room2, sender=other_user, content="سلام", is_read=True)

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("apps.chat:chatroom-unread")
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == str(room1.id)


@pytest.mark.django_db
class TestChatRoomSummaryListView:
    def test_chat_room_summary_list_view_returns_expected_data(self):
        user = UserFactory()
        opponent = UserFactory()
        other_user = UserFactory()

        # روم ۱ - با پیام نخونده
        room1 = ChatRoomModel.objects.create()
        room1.participants.set([user, opponent])
        MessageModel.objects.create(room=room1, sender=opponent, content="سلام تویی؟", is_read=False)

        # روم ۲ - پیام خونده شده
        room2 = ChatRoomModel.objects.create()
        room2.participants.set([user, other_user])
        MessageModel.objects.create(room=room2, sender=other_user, content="سلام رفیق", is_read=True)

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("apps.chat:chatroom-summary")  # مطمئن شو همین نام در urls.py ثبت شده

        response = client.get(url)
        assert response.status_code == 200
        data = response.data

        # باید دو Room داشته باشیم
        assert len(data) == 2

        # بررسی ساختار یکی از Roomها
        room_data = data[0]
        assert "id" in room_data
        assert "opponent" in room_data
        assert "last_message" in room_data
        assert "unread_count" in room_data
        assert isinstance(room_data["unread_count"], int)