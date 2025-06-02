from apps.core.exceptions import APIException
from . import text


class PermissionDenied(APIException):
    status_code = 403
    default_code = 'permission_denied'
    message = text.permission_denied


class NotCreateTeam(APIException):
    status_code = 500
    default_code = 'not_create_team'
    message = text.not_create_team


class NotFoundTeam(APIException):
    status_code = 404
    default_code = 'not_found_team'
    message = text.not_found_team

