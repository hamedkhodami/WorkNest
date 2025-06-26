# tests/logbook/test_signals.py
import pytest

from apps.task.tests.factories import TaskFactory, TaskListFactory
from apps.board.tests.factories import BoardFactory
from apps.team.tests.factories import TeamFactory
from apps.logbook.models import LogEntryModel
from apps.logbook.enums import LogEventEnum


@pytest.mark.django_db
def test_task_log_created_without_actor():
    team = TeamFactory()
    board = BoardFactory(team=team)
    task_list = TaskListFactory(board=board)
    task = TaskFactory(task_list=task_list)

    log = LogEntryModel.objects.filter(
        event=LogEventEnum.TASK_CREATE,
        target_id=task.id
    ).first()

    assert log is not None
    assert log.actor is None
    assert log.team == team
    assert log.board == board
    assert log.target_repr == task.title
