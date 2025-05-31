import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from apps.team.models import TeamModel, TeamMembership
from apps.team.tests.factories import TeamFactory
from apps.account.tests.factories import UserFactory
from ....apps.team import text


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

