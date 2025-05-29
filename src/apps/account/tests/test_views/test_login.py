import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from apps.account.tests.factories import UserFactory


@pytest.mark.django_db
def test_login_basic():
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
