from django.core.exceptions import ValidationError as _ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions as _exceptions
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "status_code": response.status_code,
            "error": response.data
        }
        response.data = custom_data

    return response

class APIException(_exceptions.APIException):
    message = None

    def __init__(self, detail=None, code=None, message=None):
        self.detail = None
        if isinstance(detail, Exception):
            self.detail = str(detail)
        self.default_detail = {"code": self.default_code, "message": message or self.message}
        if self.detail:
            self.default_detail.update({
                "detail": self.detail
            })
        super().__init__(self.default_detail, code)

ValidationError = _ValidationError

class ValidationErrorAPI(APIException):
    status_code = 400
    default_code = 'validation_error'
    message = _('Validation error')

class OperationHasAlreadyBeenDoneError(APIException):
    status_code = 409
    default_code = 'operation_has_already_been_done'
    message = _("The operation has already been done")

class FieldIsRequired(APIException):
    status_code = 400
    default_code = 'field_is_required'
    message = _("Field is required")

class FieldIsNotValid(APIException):
    status_code = 400
    default_code = 'field_is_invalid'
    message = _("Field is not valid")

class AppSectionDisabled(APIException):
    status_code = 403
    default_code = 'app_section_disabled'
    message = _("App section disabled")



