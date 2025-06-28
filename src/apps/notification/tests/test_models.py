import pytest
from django.utils import timezone
from apps.notification.models import NotificationStatus
from apps.notification.tests.factories import NotificationFactory


@pytest.mark.django_db
class TestNotificationModel:

    def test_create_notification(self):
        notif = NotificationFactory()
        assert notif.pk is not None
        assert notif.status == NotificationStatus.PENDING

    def test_get_title_and_content(self):
        notif = NotificationFactory(title="Test Title", description="This is a test.")
        assert notif.get_title() == "Test Title"
        assert "Test Title" in notif.get_content()
        assert "This is a test." in notif.get_content()

    def test_get_link_from_kwargs(self):
        notif = NotificationFactory(kwargs={"link": "https://example.com"})
        assert notif.get_link() == "https://example.com"

    def test_get_link_invalid_kwargs(self):
        notif = NotificationFactory(kwargs=None)
        assert notif.get_link() is None

    def test_sent_at_field_auto(self):
        notif = NotificationFactory()
        assert isinstance(notif.sent_at, timezone.datetime)