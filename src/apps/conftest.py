import pytest
from apps.account.tests.factories import UserFactory

@pytest.fixture
def test_user():
    return UserFactory()

@pytest.fixture
def test_admin():
    return UserFactory(role="admin")

@pytest.fixture
def test_project_member():
    return UserFactory(role="project_member")
