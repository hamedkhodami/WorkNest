# test/test_models.py
import pytest
from ..models import User, UserProfileModel, UserBlock
from .factories import UserFactory, UserProfileFactory, UserBlockFactory


@pytest.mark.django_db
class TestUserModel:

    def test_user_creation(self):
        user = UserFactory()
        assert user.phone_number is not None
        assert user.role == User.Role.VIEWER
        assert user.check_password("testpass123")

    def test_user_str(self):
        user = UserFactory(email="test@example.com")
        assert str(user) == f"{user.phone_number} - test@example.com"

    def test_user_full_name(self):
        user = UserFactory(first_name="علی", last_name="رضایی")
        assert user.full_name() == "علی رضایی"

    def test_user_is_blocked_property(self):
        user = UserFactory()
        assert user.is_blocked is False

        # حالا بلاک می‌کنیم
        UserBlockFactory(user=user)
        assert user.is_blocked is True

    def test_national_id_check(self):
        user = UserFactory()
        result = user.national_id_check(user.phone_number, user.national_id)
        assert result is True

        result_false = user.national_id_check("09120000000", "00000000000")
        assert result_false is False

    def test_national_id_check_by_data(self):
        user = UserFactory()
        assert user.national_id_check_by_data(user.phone_number, user.national_id) is True
        assert user.national_id_check_by_data("fake", "fake") is False


@pytest.mark.django_db
class TestUserProfileModel:

    def test_profile_creation_and_str(self):
        profile = UserProfileFactory()
        assert str(profile) == str(profile.user)

    def test_profile_picture_default(self):
        profile = UserProfileFactory(image=None)
        assert profile.get_profile_picture_url().endswith("default/profile.jpg")


@pytest.mark.django_db
class TestUserBlockModel:

    def test_user_block_creation(self):
        block = UserBlockFactory()
        assert str(block) == str(block.user)
        assert block.is_blocked_by_admin(block.admin) is True