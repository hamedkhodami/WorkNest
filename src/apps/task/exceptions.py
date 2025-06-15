from apps.core.exceptions import APIException
from apps.core import text


class NotFoundTeam(APIException):
    status_code = 400
    default_code = 'not_found_team'
    message = text.not_found

