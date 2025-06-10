import pytest

from apps.team.tests.factories import TeamFactory
from apps.account.tests.factories import UserFactory
from apps.team.models import TeamMembership, TeamJoinRequest


@pytest.mark.django_db
class TestTeamModel:

    def test_member_count(self):
        team = TeamFactory()
        assert team.member_count() == 0

    def test_change_team_visibility(self):
        team = TeamFactory(is_public=False)
        team.change_team_visibility(True)

        assert team.is_public is True

    def test_lock_team(self):
        team = TeamFactory(is_locked=False)
        team.lock_team()

        assert team.is_locked is True


@pytest.mark.django_db
class TestTeamMembership:

    def test_team_membership_str(self):
        user = UserFactory(first_name="علی", last_name="محمدی")
        team = TeamFactory(name="تیم تستی")
        membership = TeamMembership.objects.create(user=user, team=team, responsible="Manager")

        assert str(membership) == f"{user.full_name()} - تیم تستی"

    def test_is_member(self):
        user = UserFactory()
        team = TeamFactory()
        TeamMembership.objects.create(user=user, team=team)

        assert TeamMembership.is_member(user, team) is True
        assert TeamMembership.is_member(UserFactory(), team) is False


@pytest.mark.django_db
class TestTeamMembership:
    def test_team_join_request(self):
        user = UserFactory()
        team = TeamFactory()

        request = TeamJoinRequest.objects.create(user=user, team=team, status=TeamJoinRequest.STATUS_CHOICES.PENDING)

        assert request.user == user
        assert request.team == team
        assert request.status == TeamJoinRequest.STATUS_CHOICES.PENDING
        assert str(request) == f"{team.name} - {TeamJoinRequest.STATUS_CHOICES.PENDING}"


