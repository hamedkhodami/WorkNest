import pytest
from apps.account.models import UserProfileModel
from apps.account.tests.factories import UserFactory


@pytest.mark.django_db
class TestSignal:
    def test_user_post_save_creates_profile(self):
        user = UserFactory()

        profile = UserProfileModel.objects.filter(user=user).first()

        assert profile is not None
        assert profile.user == user
