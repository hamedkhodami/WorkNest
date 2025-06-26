import pytest
from apps.logbook.tests.factories import LogEntryFactory
from apps.logbook.enums import LogEventEnum


@pytest.mark.django_db
def test_log_entry_factory_creates_valid_entry():
    log_entry = LogEntryFactory()

    assert log_entry.pk is not None
    assert log_entry.event in dict(LogEventEnum.choices)
    assert log_entry.actor is not None
    assert log_entry.team is not None
    assert log_entry.board is not None
    assert log_entry.target_id is not None
    assert log_entry.target_repr
    assert isinstance(log_entry.extra_data, dict)

