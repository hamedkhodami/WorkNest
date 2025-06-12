from apps.core.exceptions import APIException
from apps.core import text


class NotCreateBoard(APIException):
    status_code = 500
    default_code = 'not_create_team'
    message = text.not_create


class NotTeam(APIException):
    status_code = 400
    default_code = 'not_team'
    message = text.not_team


class NotFoundTeam(APIException):
    status_code = 404
    default_code = 'not_found_board_team'
    message = text.not_found


class NotFoundBoard(APIException):
    status_code = 404
    default_code = 'not_found_board'
    message = text.not_found
