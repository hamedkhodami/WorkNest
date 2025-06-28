import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils.timezone import now, timedelta

from apps.logbook.tests.factories import LogEntryFactory
from apps.team.tests.factories import TeamFactory, TeamMembershipFactory
from apps.board.tests.factories import BoardFactory
from apps.account.tests.factories import UserFactory

from apps.logbook.enums import LogEventEnum


@pytest.mark.django_db
class TestLogEntryAPI:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, team_user=True)
        self.team = TeamFactory()
        self.board = BoardFactory(team=self.team)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.logs = LogEntryFactory.create_batch(5, team=self.team, board=self.board)

        LogEntryFactory.create_batch(3)

        self.client.force_authenticate(user=self.user)

    def test_list_logs(self):
        url = reverse("logbook:log-list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.data["data"]) == 8

    def test_filter_logs_by_team(self):
        url = reverse("logbook:log-list") + f"?team={self.team.id}"
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.data["data"]) == 5

    def test_filter_logs_by_board(self):
        url = reverse("logbook:log-list") + f"?board={self.board.id}"
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.data["data"]) == 5

    def test_access_control(self):
        other_user = UserFactory()
        self.client.force_authenticate(user=other_user)

        url = reverse("logbook:log-list") + f"?team={self.team.id}"
        response = self.client.get(url)

        assert response.status_code == 403


@pytest.mark.django_db
class TestLogbookDashboardView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, team_user=True)
        self.team = TeamFactory()
        self.board = BoardFactory(team=self.team)
        TeamMembershipFactory(user=self.user, team=self.team)
        self.client.force_authenticate(user=self.user)

        for days_ago in range(3):
            LogEntryFactory.create_batch(
                2,
                actor=self.user,
                team=self.team,
                board=self.board,
                created_at=now() - timedelta(days=days_ago),
                event=LogEventEnum.TASK_UPDATE,
            )

    def test_dashboard_returns_valid_response(self):
        url = reverse("logbook:logbook-dashboard")
        response = self.client.get(url, {"team": str(self.team.id)})

        assert response.status_code == status.HTTP_200_OK
        assert "activity_trend" in response.data
        assert "top_actors" in response.data
        assert "popular_boards" in response.data

    def test_activity_trend_structure(self):
        url = reverse("logbook:logbook-dashboard")
        response = self.client.get(url, {"team": str(self.team.id)})

        trend = response.data["activity_trend"]
        assert isinstance(trend, list)
        assert all("date" in item and "count" in item for item in trend)

    def test_top_actors_data(self):
        url = reverse("logbook:logbook-dashboard")
        response = self.client.get(url, {"team": str(self.team.id)})

        actors = response.data["top_actors"]
        assert len(actors) == 1
        assert actors[0]["user_id"] == str(self.user.id)
        assert actors[0]["activity_count"] == 6

    def test_access_denied_for_non_member(self):
        other_user = UserFactory()
        self.client.force_authenticate(user=other_user)

        url = reverse("logbook:logbook-dashboard")
        response = self.client.get(url, {"team": str(self.team.id)})

        assert response.status_code == status.HTTP_403_FORBIDDEN