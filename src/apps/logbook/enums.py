from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class LogEventEnum(TextChoices):
    TASK_CREATE = "task_create", _("Task created")
    TASK_UPDATE = "task_update", _("Task updated")
    TASK_DELETE = "task_delete", _("Task deleted")
    BOARD_CREATE = "board_create", _("Board created")
    BOARD_UPDATE = "board_update", _("Board updated")
    BOARD_ARCHIVE = "board_archive", _("Board archived/restore")
    TEAM_MEMBER_ADD = "team_member_add", _("Team member added")
    TEAM_MEMBER_DROP = "team_member_drop", _("Team member removed")
    USER_SIGNUP = "user_signup", _("User signed up")
    USER_LOGIN = "user_login", _("User logged in")
    USER_LOGOUT = "user_logout", _("User logged out")
    PROFILE_UPDATE = "profile_update", _("Profile updated")
