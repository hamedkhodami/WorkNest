import pytest
from uuid import uuid4
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from apps.account.tests.factories import UserFactory
from apps.account.enums import UserRoleEnum as Role
from apps.team.tests.factories import TeamFactory, TeamMembershipFactory
from apps.task.tests.factories import TaskListFactory, TaskFactory
from apps.board.tests.factories import BoardFactory


@pytest.mark.django_db
class TestTaskListCreationView:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role="admin")
        self.team = TeamFactory(created_by=self.user)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:task-create")

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
class TestTaskListDetailView:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, team_user=True)
        self.team = TeamFactory(created_by=self.user)
        self.board = BoardFactory(team=self.team)
        self.tasklist = TaskListFactory(board=self.board)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:tasklist-detail", kwargs={'tasklist_id': self.tasklist.id})

    def test_tasklist_detail_success(self):

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.data["title"] == self.tasklist.title
        assert response.data["description"] == self.tasklist.description
        assert response.data["order"] == self.tasklist.order

    def test_tasklist_detail_not_found(self):
        url = reverse('apps.team:team-detail',  kwargs={'team_id': uuid4()})
        response = self.client.get(url)

        assert response.status_code == 404

    def test_detail_board_forbidden_for_non_team_user(self):
        outsider = UserFactory(is_active=True, role=Role.VIEWER)
        self.client.force_authenticate(user=outsider)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCreateTaskAndAssignToUser:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = UserFactory(is_active=True, project_admin=True)
        self.assignee = UserFactory(is_active=True)
        self.team = TeamFactory(created_by=self.admin)
        self.board = BoardFactory(team=self.team)
        self.task_list = TaskListFactory(board=self.board)

        TeamMembershipFactory(user=self.admin, team=self.team)
        TeamMembershipFactory(user=self.assignee, team=self.team)

        self.client.force_authenticate(user=self.admin)
        self.url = reverse("task:assign-task-to-user")

    def test_admin_creates_task_for_user_successfully(self):
        task_data = TaskFactory.build(task_list=self.task_list, assignee=self.assignee)

        payload = {
            "title": task_data.title,
            "description": task_data.description,
            "deadline": task_data.deadline.isoformat() if task_data.deadline else None,
            "priority": task_data.priority,
            "task_list": self.task_list.id,
            "assignee": self.assignee.id
        }

        response = self.client.post(self.url, payload, format="json")
        print("Response:", response.data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == payload["title"]
        assert response.data["assignee"]["name"] == self.assignee.full_name()
        assert response.data["task_list"]["name"] == self.task_list.title


@pytest.mark.django_db
class TestRemoveTaskView:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role="admin")
        self.team = TeamFactory()
        self.board = BoardFactory(team=self.team)
        self.task_list = TaskListFactory(board=self.board)
        self.task = TaskFactory(task_list=self.task_list)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:remove-task")

    def test_remove_task_success(self):
        response = self.client.delete(
            self.url,
            {
                "id": str(self.task.id),
                "task_list_id": str(self.task_list.id)
            },
            format="json"
        )

        assert not TaskListFactory._meta.model.objects.filter(id=self.task.id).exists()


@pytest.mark.django_db
class TestTaskDetailView:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, team_user=True)
        self.team = TeamFactory(created_by=self.user)
        self.board = BoardFactory(team=self.team)
        self.task_list = TaskListFactory(board=self.board)
        self.task = TaskFactory(task_list=self.task_list)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:task-detail", kwargs={'task_id': self.task.id})

    def test_task_detail_success(self):

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.data["title"] == self.task.title
        assert response.data["description"] == self.task.description
        assert response.data["is_done"] == self.task.is_done
        assert response.data["deadline"] == self.task.deadline.isoformat(timespec="seconds")
        assert response.data["priority"] == self.task.priority
        assert response.data["task_list"]["name"] == self.task.task_list.title
        assert response.data["assignee"]["name"] == self.task.assignee.full_name()

    def test_detail_task_forbidden_for_non_team_user(self):
        outsider = UserFactory(is_active=True, role=Role.VIEWER)
        self.client.force_authenticate(user=outsider)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTaskUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = UserFactory(is_active=True, is_superuser=False, role=Role.PROJECT_MEMBER)
        self.admin = UserFactory(is_active=True, is_superuser=True, role=Role.ADMIN)
        self.team = TeamFactory()
        self.board = BoardFactory(team=self.team)
        self.task_list = TaskListFactory(board=self.board)
        self.task = TaskFactory(task_list=self.task_list)

        TeamMembershipFactory(user=self.user, team=self.team)

        self.client.force_authenticate(user=self.user)
        self.url = reverse("task:task-update", kwargs={'task_id': self.task.id})

    def test_update_task_success(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "title": "Updated task",
            "description": "Updated Description",
        }
        response = self.client.put(self.url, data)

        assert response.status_code == 200
        self.board.refresh_from_db()

    def test_update_task_permission_denied(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "Unauthorized Update"}
        response = self.client.put(self.url, data)

        assert response.status_code == 403

    def test_update_task_not_found(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("task:task-update", kwargs={"task_id": "00000000-0000-0000-0000-000000000000"})
        response = self.client.put(url, {"title": "New Title"})
        assert response.status_code == 404





