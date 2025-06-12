import pytest
from apps.team.models import TeamJoinRequest, TeamMembership
from apps.account.tests.factories import UserFactory
from apps.team.tests.factories import TeamFactory, TeamMembershipFactory, TeamJoinRequestFactory
from apps.team.enums import JoinTeamStatusEnum


@pytest.mark.django_db
def test_signal_creates_membership():
    user = UserFactory(is_active=True)
    team = TeamFactory(created_by=user)
    join_request = TeamJoinRequestFactory(user=user, team=team, status=JoinTeamStatusEnum.PENDING)

    join_request.status = JoinTeamStatusEnum.ACCEPTED
    join_request.save()

    assert TeamMembership.objects.filter(user=user, team=team).exists()


@pytest.mark.django_db
def test_signal_updates_user_role_on_membership_change():
    user = UserFactory(is_active=True)
    team = TeamFactory(created_by=user)
    membership = TeamMembershipFactory(user=user, team=team)

    membership.save()

    membership.delete()
