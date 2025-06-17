import pytest
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from apps.board.models import BoardModel
from apps.account.tests.factories import UserFactory
from apps.account.enums import UserRoleEnum as Role
from apps.team.tests.factories import TeamFactory, TeamMembershipFactory
from apps.task.tests.factories import TaskListFactory, TaskFactory
from apps.board.tests.factories import BoardFactory


@pytest.mark.django_db
class TestTaskCreationView:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role="admin")
        self.team = TeamFactory(created_by=self.user)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:task-create")

    def test_create_task_list_success(self):
        """ بررسی ایجاد موفق لیست وظایف """
        board = BoardFactory(team=self.team)  # ایجاد یک Board مرتبط با تیم
        task_list = TaskListFactory(board=board)  # مقداردهی صحیح فیلد `board`

        response = self.client.post(
            self.url,
            {
                "title": task_list.title,
                "description": task_list.description,
                "order": task_list.order,
                "team_id": self.team.id
            },
            format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == task_list.title
        assert response.data["description"] == task_list.description
        assert TaskListFactory._meta.model.objects.filter(title=task_list.title,
                                                          board=board).exists()  # تغییر مقدار `board`

    def test_create_task_list_without_team(self):
        response = self.client.post(
            self.url,
            {
                "title": "Task List Without Team",
                "description": "Should fail",
                "order": 1
            },
            format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST  # حالا مقدار صحیح بررسی می‌شود
        assert "error" in response.data


@pytest.mark.django_db
class TestTaskListDeleteView:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role="admin")
        self.team = TeamFactory(created_by=self.user)
        self.board = BoardFactory(team=self.team)
        self.tasklist = TaskListFactory(board=self.board)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:task-delete")

    def test_delete_task_list_success(self):
        response = self.client.delete(
            self.url,
            {
                "id": str(self.tasklist.id),
                "board_id": str(self.board.id)
            },
            format="json"
        )

        assert not TaskListFactory._meta.model.objects.filter(id=self.tasklist.id).exists()

    def test_delete_task_list_not_found(self):
        response = self.client.delete(
            self.url,
            {
                "id": "00000000-0000-0000-0000-000000000000",  # مقدار نامعتبر
                "board_id": str(self.board.id)
            },
            format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_list_without_board(self):
        response = self.client.delete(
            self.url,
            {
                "id": str(self.tasklist.id)
            },
            format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "board_id" in response.data["error"]  # بررسی مقدار داخل `error`


@pytest.mark.django_db
class TestTaskListsView:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, team_user=True)
        self.team = TeamFactory(created_by=self.user)
        self.board = BoardFactory(team=self.team)
        self.tasklist_1 = TaskListFactory(board=self.board)
        self.tasklist_2 = TaskListFactory(board=self.board)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:task-list")

    def test_get_task_lists_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 2
        assert response.data["data"][0]["uuid"] == str(self.tasklist_1.uuid)
        assert response.data["data"][1]["uuid"] == str(self.tasklist_2.uuid)

    def test_get_task_lists_filtered_by_board(self):
        response = self.client.get(self.url, {"board_id": str(self.board.id)})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 2

    def test_get_task_lists_with_invalid_board(self):
        response = self.client.get(self.url, {"board_id": "00000000-0000-0000-0000-000000000000"})

        assert response.status_code == status.HTTP_404_NOT_FOUND