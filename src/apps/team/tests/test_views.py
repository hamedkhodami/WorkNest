import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from apps.team.models import TeamModel, TeamMembership
from apps.account.tests.factories import UserFactory
from apps.team.tests.factories import TeamFactory, TeamMembershipFactory
from apps.team import text


@pytest.mark.django_db
class TestTeamCreateView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("apps.team:team_create")

    def test_create_team_success(self):
        data = {"name": "Awesome Team", "description": "Best team ever!", "is_public": True}
        response = self.client.post(self.url, data)

        assert response.status_code == 201
        assert TeamModel.objects.filter(name="Awesome Team").exists()
        assert TeamMembership.objects.filter(user=self.user, team__name="Awesome Team", responsible="Owner").exists()

    def test_create_team_duplicate_name(self):
        TeamFactory(name="Duplicate Team")
        data = {"name": "Duplicate Team", "description": "Trying to reuse the name", "is_public": True}
        response = self.client.post(self.url, data)

        assert response.status_code == 400
        assert str(response.data["name"][0]) == str(text.team_registered)

    def test_create_team_without_authentication(self):
        self.client.force_authenticate(user=None)
        data = {"name": "NoAuth Team", "description": "Testing without login", "is_public": True}
        response = self.client.post(self.url, data)

        assert response.status_code == 401


@pytest.mark.django_db
class TestUserTeamsView:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("apps.team:user_teams")  # مسیر صحیح را بررسی کن

    def test_user_teams_success(self):
        """ تست بررسی دریافت تیم‌های کاربر با موفقیت """
        team1 = TeamFactory(name="Team One")
        team2 = TeamFactory(name="Team Two")
        TeamMembershipFactory(user=self.user, team=team1)
        TeamMembershipFactory(user=self.user, team=team2)

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert "teams" in response.data  # بررسی وجود کلید در پاسخ API
        assert len(response.data["teams"]) == 2
        assert response.data["teams"][0]["team_name"] == "Team One"
        assert response.data["teams"][1]["team_name"] == "Team Two"

    def test_user_without_teams(self):
        """ تست بررسی کاربری که عضو هیچ تیمی نیست """
        response = self.client.get(self.url)

        assert response.status_code == 200
        assert "teams" in response.data  # بررسی وجود کلید در پاسخ API
        assert response.data["teams"] == []

    def test_user_without_authentication(self):
        """ تست بررسی درخواست بدون احراز هویت """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        assert response.status_code == 401
