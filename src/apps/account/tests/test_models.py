import pytest
from apps.account.models import UserBlock, UserProfileModel
from apps.account.tests.factories import UserFactory

@pytest.mark.django_db
def test_user_full_name():
    user = UserFactory(first_name="حامد", last_name="برنامه‌نویس")
    assert user.full_name() == "حامد برنامه‌نویس"

@pytest.mark.django_db
def test_user_is_admin_project_user():
    user = UserFactory(role="project_admin")
    assert user.is_admin_project_user is True

@pytest.mark.django_db
def test_user_blocking():
    user = UserFactory(role="viewer")
    admin = UserFactory(role="admin")
    user_block = UserBlock.objects.create(user=user, admin=admin, note="Test block")

    assert user.is_blocked is True
    assert user_block.admin == admin

@pytest.mark.django_db
def test_user_profile_creation():
    user = UserFactory()
    user.refresh_from_db()
    assert hasattr(user, "profile")

    assert user.profile.gender is None
    assert user.profile.bio is None