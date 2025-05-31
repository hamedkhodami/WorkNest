from apps.core.exceptions import APIException
from . import text


class PermissionDenied(APIException):
    status_code = 403
    default_code = 'team_registered'
    message = text.permission_denied


class NotCreateTeam(APIException):
    status_code = 500
    default_code = 'team_registered'
    message = text.not_create_team

