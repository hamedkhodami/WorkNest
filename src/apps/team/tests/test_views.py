import uuid
import pytest
from rest_framework.test import APIClient
from uuid import uuid4
from django.urls import reverse

from apps.core import text

from apps.team.models import TeamModel, TeamMembership, TeamInvitation, TeamJoinRequest
from apps.account.tests.factories import UserFactory
from apps.team.tests.factories import TeamFactory, TeamMembershipFactory, TeamJoinRequestFactory, TeamInvitationFactory
from apps.account.enums import UserRoleEnum as Role
from apps.team.enums import JoinTeamStatusEnum


STATUS_CHOICES = JoinTeamStatusEnum


@pytest.mark.django_db
class TestTeamCreateView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role=Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("apps.team:team_create")

    def test_create_team_success(self):
        data = {"name": "Awesome Team", "description": "Best team ever!"}
        response = self.client.post(self.url, data)

        assert response.status_code == 201
        assert TeamModel.objects.filter(name="Awesome Team", created_by=self.user).exists()

    def test_create_team_without_authentication(self):
        self.client.force_authenticate(user=None)
        data = {"name": "NoAuth Team", "description": "Testing without login"}
        response = self.client.post(self.url, data)

        assert response.status_code == 401


@pytest.mark.django_db
class TestUserTeamsView:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("apps.team:user_teams")

    def test_user_teams_success(self):
        team1 = TeamFactory(name="Team One")
        team2 = TeamFactory(name="Team Two")
        TeamMembershipFactory(user=self.user, team=team1)
        TeamMembershipFactory(user=self.user, team=team2)

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert "teams" in response.data
        assert len(response.data["teams"]) == 2
        assert response.data["teams"][0]["team_name"] == "Team One"
        assert response.data["teams"][1]["team_name"] == "Team Two"

    def test_user_without_teams(self):
        response = self.client.get(self.url)

        assert response.status_code == 200
        assert "teams" in response.data
        assert response.data["teams"] == []

    def test_user_without_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        assert response.status_code == 401


@pytest.mark.django_db
class TestTeamDetailView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.client.force_authenticate(user=self.user)

    def test_team_detail_success(self):
        team = TeamFactory()
        TeamMembershipFactory(user=self.user, team=team)

        url = reverse('apps.team:team-detail', kwargs={'team_id': team.id})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == str(team.id)
        assert response.data["name"] == team.name
        assert response.data["description"] == team.description
        assert response.data["member_count"] == team.member_count()
        assert isinstance(response.data["members"], list)

    def test_team_detail_not_found(self):
        url = reverse('apps.team:team-detail',  kwargs={'team_id': uuid4()})
        response = self.client.get(url)

        assert response.status_code == 404

    def test_team_detail_unauthenticated(self):
        self.client.force_authenticate(user=None)
        team = TeamFactory()
        url = reverse('apps.team:team-detail', kwargs={'team_id': team.id})
        response = self.client.get(url)

        assert response.status_code == 401


@pytest.mark.django_db
class TestTeamUpdateView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, is_superuser=False, role=Role.PROJECT_MEMBER)
        self.admin = UserFactory(is_active=True, is_superuser=True,role=Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.team = TeamFactory(name="Test Team")
        self.url = reverse("team:team-update", kwargs={"team_id": self.team.id})

    def test_update_team_success(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Updated Team", "description": "Updated Description"}
        response = self.client.put(self.url, data)

        assert response.status_code == 200
        self.team.refresh_from_db()
        assert self.team.name == "Updated Team"

    def test_update_team_permission_denied(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Unauthorized Update"}
        response = self.client.put(self.url, data)

        assert response.status_code == 403


@pytest.mark.django_db
class TestJoinTeamView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, viewer=True)
        self.client.force_authenticate(user=self.user)

    def test_join_team_success(self):
        team = TeamFactory(is_locked=False)

        url = reverse('team:team-join')
        response = self.client.post(url, {"team": team.id, "user": self.user.id})

        assert response.status_code == 201
        assert response.data["message"] == text.success_team_request

    def test_join_locked_team(self):
        team = TeamFactory(is_locked=True)

        url = reverse('team:team-join')
        response = self.client.post(url, {"team": team.id, "user": self.user.id})

        assert response.status_code == 403
        assert response.data["message"] == text.team_locked

    def test_join_team_unauthenticated(self):
        self.client.force_authenticate(user=None)
        team = TeamFactory(is_locked=False)

        url = reverse('team:team-join')
        response = self.client.post(url, {"team": team.id, "user": self.user.id})

        assert response.status_code == 401


@pytest.mark.django_db
class TestResolveJoinRequestView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role=Role.ADMIN)
        self.team = TeamFactory(created_by=self.user)
        self.request = TeamJoinRequestFactory(user=self.user, team=self.team, status=JoinTeamStatusEnum.PENDING)

        self.url = reverse("team:resolve-join-request", kwargs={"pk": self.request.pk})

        self.client.force_authenticate(user=self.user)

        TeamMembership.objects.filter(user=self.user, team=self.team).delete()

    def test_reject_join_request(self):
        data = {"status": JoinTeamStatusEnum.REJECTED}
        response = self.client.post(self.url, data)

        assert response.status_code == 200
        assert not TeamMembership.objects.filter(user=self.user, team=self.team).exists()

    def test_request_not_found(self):
        invalid_url = reverse("team:resolve-join-request", kwargs={"pk": 99999})
        response = self.client.post(invalid_url, {"status": JoinTeamStatusEnum.ACCEPTED})

        assert response.status_code == 404

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {"status": JoinTeamStatusEnum.ACCEPTED})

        assert response.status_code == 401


@pytest.mark.django_db
class TestResultInvitationTeamView:

    def setup_method(self):
        self.client = APIClient()
        self.invitee = UserFactory(is_active=True, viewer=True)
        self.team = TeamFactory()
        self.join_request = TeamInvitationFactory(invitee=self.invitee, team=self.team, status=JoinTeamStatusEnum.PENDING)

        self.url = reverse("team:team-resolve-invite", kwargs={"pk": self.join_request.pk})
        self.client.force_authenticate(user=self.invitee)

    def test_accept_invitation_success(self):
        data = {"status": JoinTeamStatusEnum.ACCEPTED}
        response = self.client.post(self.url, data)

        assert response.status_code == 200
        assert TeamMembership.objects.filter(user=self.invitee, team=self.team).exists()

    def test_reject_invitation_success(self):
        data = {"status": JoinTeamStatusEnum.REJECTED}
        response = self.client.post(self.url, data)

        assert response.status_code == 200
        assert not TeamMembership.objects.filter(user=self.invitee, team=self.team).exists()

    def test_invitation_not_found(self):
        invalid_url = reverse("team:team-resolve-invite", kwargs={"pk": uuid.uuid4()})
        response = self.client.post(invalid_url, {"status": JoinTeamStatusEnum.ACCEPTED})

        assert response.status_code == 404

    def test_unauthorized_access(self):
        another_user = UserFactory(is_active=True)
        self.client.force_authenticate(user=another_user)

        response = self.client.post(self.url, {"status": JoinTeamStatusEnum.ACCEPTED})

        assert response.status_code == 403


@pytest.mark.django_db
class TestUserTeamRequestView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.team = TeamFactory()
        self.invitation = TeamInvitationFactory(invitee=self.user, team=self.team, status=STATUS_CHOICES.PENDING)
        self.join_request = TeamJoinRequestFactory(user=self.user, team=self.team, status=STATUS_CHOICES.PENDING)

        self.url = reverse("team:user-team-requests")
        self.client.force_authenticate(user=self.user)

    def test_get_user_requests_success(self):
        response = self.client.get(self.url)

        assert response.status_code == 200
        data = response.json()["data"]
        assert any(req["type"] == "INVITATION" and req["user"] == self.user.full_name() for req in data)
        assert any(req["type"] == "JOIN_REQUEST" and req["user"] == self.user.full_name() for req in data)

    def test_no_requests(self):
        TeamInvitation.objects.filter(invitee=self.user).delete()
        TeamJoinRequest.objects.filter(user=self.user).delete()

        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        assert response.status_code == 401



