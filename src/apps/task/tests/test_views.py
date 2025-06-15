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
        """ تنظیمات اولیه تست‌ها """
        self.client = APIClient()
        self.user = UserFactory(is_active=True, role="admin")
        self.team = TeamFactory(created_by=self.user)

        # ایجاد عضویت کاربر در تیم
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

