import pytest
from rest_framework_simplejwt.tokens import AccessToken
from apps.account.auth.authentication import BaseJWTAuthentication
from apps.account.tests.factories import UserFactory


@pytest.mark.django_db
@pytest.mark.django_db
def test_jwt_authentication_success():
    user = UserFactory()
    auth = BaseJWTAuthentication()

    access_token = str(AccessToken.for_user(user))

