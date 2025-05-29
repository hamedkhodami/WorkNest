import pytest
from apps.account.tests.factories import UserFactory

@pytest.fixture
def test_user():
    return UserFactory()