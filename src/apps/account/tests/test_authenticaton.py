import pytest
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.account.tests.factories import UserFactory


@pytest.mark.django_db
def test_jwt_authentication_success():
    user = UserFactory()
    token = AccessToken.for_user(user)

    auth = JWTAuthentication()
    validated_user = auth.get_user(token)

    assert validated_user is not None
    assert validated_user.id == user.id