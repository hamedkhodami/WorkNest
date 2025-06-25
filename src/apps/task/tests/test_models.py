import pytest
from apps.task.tests.factories import TaskListFactory, TaskFactory
from django.utils.timezone import now, timedelta

from apps.task import enums

Priority = enums.TaskPriorityEnum


@pytest.mark.django_db
class TestTaskListModel:

    def test_create_task_list(self):
        task_list = TaskListFactory()
        assert task_list.title is not None
        assert task_list.order >= 0

    def test_get_tasks(self):
        task_list = TaskListFactory()
        task1 = TaskFactory(task_list=task_list)
        task2 = TaskFactory(task_list=task_list)

        tasks = task_list.get_tasks()
        assert tasks.count() == 2
        assert task1 in tasks
        assert task2 in tasks


@pytest.mark.django_db
class TestTaskModel:

    def test_create_task(self):
        task = TaskFactory()
        assert task.title is not None
        assert task.priority in Priority.values

    def test_mark_as_done(self):
        task = TaskFactory(is_done=False)
        task.mark_as_done()

        assert task.is_done is True
        assert task.completed_at is not None

    def test_is_overdue(self):
        overdue_task = TaskFactory(deadline=now() - timedelta(days=1), is_done=False)
        valid_task = TaskFactory(deadline=now() + timedelta(days=5), is_done=False)

        assert overdue_task.is_overdue() is True
        assert valid_task.is_overdue() is False

