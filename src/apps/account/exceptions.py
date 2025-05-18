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



