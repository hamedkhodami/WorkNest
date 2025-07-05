import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.notification.tests.factories import NotificationFactory
from apps.account.tests.factories import UserFactory


@pytest.mark.django_db
class TestNotificationListView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.to_user = UserFactory()
        self.url = reverse("notification:notification-list")

    def test_notification_list_authenticated(self):
        NotificationFactory.create_batch(5, to_user=self.to_user)

        self.client.force_authenticate(user=self.to_user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert isinstance(response.data["data"], list)
        assert len(response.data["data"]) == 5

    def test_notification_list_only_for_current_user(self):
        NotificationFactory.create_batch(3, to_user=self.to_user)
        NotificationFactory.create_batch(2)

        self.client.force_authenticate(user=self.to_user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 3

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED