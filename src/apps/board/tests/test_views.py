import pytest
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from apps.board.models import BoardModel
from apps.core import text
from apps.account.tests.factories import UserFactory
from apps.account.enums import UserRoleEnum as Role
from apps.team.tests.factories import TeamFactory
from apps.board.tests.factories import BoardFactory

"""
@pytest.mark.django_db
class TestCreateBoardView:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.created_by = UserFactory(is_active=True, role=Role.ADMIN)
        self.team = TeamFactory(created_by=self.created_by)
        self.created_by.team = self.team
        self.client.force_authenticate(user=self.created_by)
        self.url = reverse("board:board-create")

    def test_create_board_success(self):
        data = {"title": "Project Board", "description": "Main board for project"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert BoardModel.objects.filter(title="Project Board", team=self.team).exists()

    def test_create_board_without_team(self):
        self.created_by.team = None
        data = {"title": "Orphan Board", "description": "Trying to create without team"}
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestBoardsTeamsView:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role=Role.PROJECT_MEMBER)
        self.team = TeamFactory(created_by=self.user)
        self.user.team = self.team
        self.client.force_authenticate(user=self.user)
        self.url = reverse("board:boards_teams")

    def test_list_boards_success(self):

        board1 = BoardFactory(title="Board One", team=self.team)
        board2 = BoardFactory(title="Board Two", team=self.team)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["title"] in ["Board One", "Board Two"]

    def test_list_boards_archived_filter(self):
        BoardFactory(title="Active Board", team=self.team, is_archived=False)
        BoardFactory(title="Archived Board", team=self.team, is_archived=True)

        response = self.client.get(f"{self.url}?is_archived=true")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Archived Board"


@pytest.mark.django_db
class TestDetailBoardView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role=Role.PROJECT_MEMBER)
        self.team = TeamFactory(created_by=self.user)
        self.user.team = self.team
        self.board = BoardFactory(team=self.team, created_by=self.user)
        self.url = reverse("board:board-detail", kwargs={"board_uuid": str(self.board.id)})

    def test_detail_board_success_for_team_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == self.board.title
        assert response.data["team"]["name"] == self.team.name

    def test_detail_board_forbidden_for_non_team_user(self):
        outsider = UserFactory(is_active=True, role=Role.VIEWER)
        self.client.force_authenticate(user=outsider)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
"""

@pytest.mark.django_db
class TestDeleteBoardView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin_user = UserFactory(is_active=True, role=Role.ADMIN)
        self.team = TeamFactory(created_by=self.admin_user)
        self.admin_user.team = self.team
        self.board = BoardFactory(team=self.team, created_by=self.admin_user)
        self.url = reverse("board:board-delete")

    def test_delete_board_success_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url, {"board_id": self.board.id, "team_id": self.team.id}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "بورد با موفقیت حذف شد."

    def test_delete_board_forbidden_for_non_admin(self):
        non_admin_user = UserFactory(is_active=True, role="viewer")
        non_admin_user.team = self.team
        self.client.force_authenticate(user=non_admin_user)

        response = self.client.delete(self.url, {"board_id": self.board.id, "team_id": self.team.id}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_board_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.delete(self.url, {"board_id": fake_uuid, "team_id": self.team.id}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == text.not_match

