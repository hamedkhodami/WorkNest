import pytest
from django.urls import reverse
from unittest import mock
from rest_framework.test import APIClient
from apps.account.models import User


@pytest.mark.django_db
class TestRegisterAPI:

    def setup_method(self):
        self.client = APIClient()
        self.phone = "+989123456789"
        self.password = "securePass123"
        self.national_id = "0012345678"
        self.user_data = {
            "phone_number": self.phone,
            "email": "user@example.com",
            "first_name": "حامد",
            "last_name": "برنامه‌نویس",
            "role": "viewer",
            "national_id": self.national_id,
            "otp_code": "1234",
            "password": self.password
        }
        self.url = reverse("apps.account:register")
        self.redis_key = f"user_otp_auth_phonenumber_{self.phone}"

    @mock.patch("apps.account.views.redis_utils.get_value", return_value=None)
    def test_registration_fails_if_otp_code_invalid(self, _):
        response = self.client.post(self.url, data=self.user_data, format="json")
        assert response.status_code == 400 or response.status_code == 403


"""
    @mock.patch("apps.account.views.redis_utils.get_value", return_value="1234")
    @mock.patch("apps.account.views.redis_utils.remove_key")
    @mock.patch("apps.account.views.create_notify")
    def test_successful_registration_returns_tokens(
        self, mock_notify, mock_remove, mock_get
    ):
        User.objects.create(
            phone_number=self.phone,
            national_id=self.national_id,
            is_active=False
        )

        self.user_data["password"] = self.password

        response = self.client.post(self.url, data=self.user_data, format="json")

        assert response.status_code == 201
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user_role"] == "viewer"
"""