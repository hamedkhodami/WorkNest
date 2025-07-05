import pytest
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from apps.account.tests.factories import UserFactory
from apps.account.enums import UserRoleEnum as Role
from apps.team.models import TeamModel


@pytest.mark.django_db
class TestViewerUser:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.url = reverse("public:user-viewer-list")

    def test_list_viewer_user_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data

    def test_list_only_viewer_users(self):
        UserFactory.create_batch(3, role=Role.VIEWER)
        UserFactory.create_batch(2, role=Role.ADMIN)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_response_fields(self):
        UserFactory.create(role=Role.VIEWER)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        user = response.data["data"][0]
        expected_fields = {"full_name", "phone_number", "email"}
        assert expected_fields.issubset(set(user.keys()))


@pytest.mark.django_db
class TestPublicTeamList:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("public:public-team-list")

    def test_list_public_teams_success(self):
        public_teams = TeamModel.objects.bulk_create([
            TeamModel(name=f"Public Team {i}", is_public=True) for i in range(15)
        ])
        private_teams = TeamModel.objects.bulk_create([
            TeamModel(name=f"Private Team {i}", is_public=False) for i in range(5)
        ])

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

        assert "data" in response.data
        assert isinstance(response.data["data"], list)
        assert len(response.data["data"]) <= 10

        for team_data in response.data["data"]:
            assert team_data["is_public"] is True
            assert team_data["visibility"] == "Public"
            assert "name" in team_data
            assert "description" in team_data

