import pytest
from unittest import mock
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.urls import reverse
from apps.account.tests.factories import UserFactory
from apps.account.models import User


@pytest.mark.django_db
class TestTokenRefreshAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.refresh_token = str(RefreshToken.for_user(self.user))
        self.url = reverse("apps.account:token_refresh")

    def test_refresh_token_success(self):
        response = self.client.post(self.url, data={"refresh": self.refresh_token}, format="json")

        assert response.status_code == 200
        assert "access" in response.data
        assert isinstance(response.data["access"], str)


@pytest.mark.django_db
class TestLoginBasicAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user_password = "testpassword123"
        self.user = UserFactory()
        self.user.set_password(self.user_password)
        self.user.save()

        self.url = reverse("apps.account:token_obtain_pair_basic")

    def test_login_basic(self):
        client = APIClient()
        user = UserFactory()
        user.set_password("TestPass123!")
        user.save()

        data = {
            "phone_number": str(user.phone_number),
            "password": "TestPass123!"
        }

        response = client.post(reverse("apps.account:token_obtain_pair_basic"), data, format="json")

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(
            self.url,
            data={"phone_number": "+989999999999", "password": "wrongpass"},
            format="json"
        )

        assert response.status_code == 401
        assert "access" not in response.data
        assert "refresh" not in response.data

    def test_login_fails_with_nonexistent_user(self):
        response = self.client.post(
            self.url,
            data={"phone_number": "+989999999999", "password": "any-password"},
            format="json"
        )

        assert response.status_code == 401


'''
@pytest.mark.django_db
class TestLoginOTPAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.phone = str(self.user.phone_number)
        self.url = reverse("apps.account:token_obtain_pair_otp")
        self.redis_key = f"otp_auth_phonenumber_{self.phone}"
        self.otp_code = "123456"

    @mock.patch("apps.account.views.redis_utils.get_value", return_value="123456")
    @mock.patch("apps.account.views.redis_utils.remove_key")
    def test_verify_otp_success_and_returns_tokens(self, mock_remove, mock_get):
        response = self.client.post(
            self.url,
            data={"phone_number": self.phone, "code": "123456"},
            format="json"
        )

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user_role"] == self.user.role

    @mock.patch("apps.account.views.redis_utils.set_value_expire")
    @mock.patch("apps.account.views.redis_utils.get_value", return_value=None)
    @mock.patch("apps.account.views.utils.random_num", return_value="123456")
    def test_send_otp_code_success(self, mock_random, mock_get, mock_set):
        response = self.client.get(self.url, data={"phone_number": self.phone})
        assert response.status_code == 200
        assert "message" in response.data

    @mock.patch("apps.account.views.redis_utils.get_value", return_value="123456")
    def test_send_otp_code_twice_should_fail(self, mock_get):
        response = self.client.get(self.url, {"phone_number": self.phone})
        assert response.status_code == 400  

    @mock.patch("apps.account.views.redis_utils.get_value", return_value="wrong-code")
    def test_verify_otp_wrong_code_fails(self, _):
        response = self.client.post(
            self.url,
            data={"phone_number": self.phone, "code": "123456"},
            format="json"
        )
        assert response.status_code == 400
'''