import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from apps.logbook.tests.factories import LogEntryFactory
from apps.team.tests.factories import TeamFactory, TeamMembershipFactory
from apps.board.tests.factories import BoardFactory
from apps.account.tests.factories import UserFactory


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

    def test_pagination(self):
        url = reverse("logbook:log-list") + "?page=1&page_size=3"
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.data["data"]) == 3

    def test_access_control(self):
        other_user = UserFactory()
        self.client.force_authenticate(user=other_user)

        url = reverse("logbook:log-list") + f"?team={self.team.id}"
        response = self.client.get(url)

        assert response.status_code == 403
