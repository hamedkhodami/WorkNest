import pytest
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from apps.board.models import BoardModel
from apps.account.tests.factories import UserFactory
from apps.account.enums import UserRoleEnum as Role
from apps.team.tests.factories import TeamFactory
from apps.board.tests.factories import BoardFactory


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
        self.url = reverse("board:board-detail", kwargs={"board_id": str(self.board.id)})


    def test_detail_board_forbidden_for_non_team_user(self):
        outsider = UserFactory(is_active=True, role=Role.VIEWER)
        self.client.force_authenticate(user=outsider)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        
@pytest.mark.django_db
class TestDeleteBoardView:

    def setup_method(self):
        self.client = APIClient()
        self.admin = UserFactory(is_active=True, role=Role.ADMIN)
        self.team = TeamFactory(created_by=self.admin)
        self.admin.team = self.team
        self.admin.save()
        self.board = BoardFactory(team=self.team, created_by=self.admin)
        self.url = reverse("board:board-delete")

    def test_delete_board_success(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "id": str(self.board.id),
            "team_id": str(self.team.id)
        }

        response = self.client.delete(self.url, data=payload, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert not BoardModel.objects.filter(id=self.board.id).exists()


@pytest.mark.django_db
class TestBoardUpdateView:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, is_superuser=False, role=Role.PROJECT_MEMBER)
        self.admin = UserFactory(is_active=True, is_superuser=True, role=Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.board = BoardFactory(title="Test Board")
        self.url = reverse("board:board-update", kwargs={"board_id": self.board.id})

    def test_update_board_success(self):
        self.client.force_authenticate(user=self.admin)
        data = {"title": "Updated Board", "description": "Updated Description"}
        response = self.client.put(self.url, data)

        assert response.status_code == 200
        self.board.refresh_from_db()
        assert self.board.title == "Updated Board"

    def test_update_board_permission_denied(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "Unauthorized Update"}
        response = self.client.put(self.url, data)

        assert response.status_code == 403

    def test_update_board_not_found(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("board:board-update", kwargs={"board_id": "00000000-0000-0000-0000-000000000000"})
        response = self.client.put(url, {"title": "New Title"})
        assert response.status_code == 404







