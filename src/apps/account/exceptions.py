from apps.core.exceptions import APIException
from . import text


class NationalIdIsNotValid(APIException):
    status_code = 400
    default_code = 'national_id_is_not_valid'
    message = text.national_id_is_not_valid


class PhoneNumberIsNotValid(APIException):
    status_code = 400
    default_code = 'phone_number_is_not_valid'
    message = text.phone_number_is_not_valid


class NationalIdNotMatch(APIException):
    status_code = 400
    default_code = 'national id not match'
    message = text.national_id_ot_match


class PhoneNumberIsNotMatchWithNationalId(APIException):
    status_code = 400
    default_code = 'phone number is not match with national id'
    message = text.phone_number_is_not_match_with_national_id


class UserNotFound(APIException):
    status_code = 404
    default_code = 'user_not_found'
    message = text.user_not_found


class CodeHasAlreadyBeenSent(APIException):
    status_code = 409
    default_code = 'code_already_has_been_send'
    message = text.code_already_has_been_send


class CodeIsWrong(APIException):
    status_code = 409
    default_code = 'code_is_wrong'
    message = text.code_is_wrong


class UserIsExists(APIException):
    status_code = 409
    default_code = 'code_is_wrong'
    message = text.user_is_exist



