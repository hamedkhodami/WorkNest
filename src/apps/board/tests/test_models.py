import pytest
from apps.board.models import BoardModel
from apps.board.tests.factories import BoardFactory
from apps.team.tests.factories import TeamFactory


@pytest.mark.django_db
class TestBoardModel:
    def test_board_creation(self):
        board = BoardFactory()
        assert isinstance(board, BoardModel), "باید یک نمونه‌ی معتبر از Board ساخته شود"
        assert board.title, "Board باید عنوان داشته باشد"
        assert board.team, "Board باید به یک تیم متصل باشد"
        assert board.created_by, "Board باید سازنده داشته باشد"

    def test_unique_title_per_team(self):
        team = TeamFactory()
        BoardFactory(title="Project A", team=team)
        with pytest.raises(Exception):
            BoardFactory(title="Project A", team=team)

    def test_board_archiving(self):
        board = BoardFactory(is_archived=False)
        assert not board.is_archived, "برد نباید از ابتدا آرشیو باشد"
        board.archive_board()
        assert board.is_archived, "بعد از فراخوانی archive_board باید آرشیو شود"

    def test_active_boards_queryset(self):
        BoardFactory(is_archived=False)
        BoardFactory(is_archived=True)
        assert BoardModel.objects.active().count() == 1, "باید فقط یک برد فعال برگردانده شود"
