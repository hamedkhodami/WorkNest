import factory
from apps.task.models import TaskListModel, TaskModel
from apps.account.tests.factories import UserFactory
from apps.board.tests.factories import BoardFactory
from apps.task import enums

Priority = enums.TaskPriorityEnum


class TaskListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskListModel

    board = factory.SubFactory(BoardFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    order = factory.Sequence(lambda n: n)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskModel

    task_list = factory.SubFactory(TaskListFactory)
    assignee = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    is_done = factory.Faker("boolean")
    order = factory.Sequence(lambda n: n)
    deadline = factory.Faker("date_time_between", start_date="-30d", end_date="+30d")
    completed_at = factory.LazyAttribute(lambda obj: obj.deadline if obj.is_done else None)
    priority = factory.Iterator([Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL])


