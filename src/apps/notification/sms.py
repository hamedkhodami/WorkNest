from .tasks import send_sms


class NotificationUser:

    @classmethod
    def handler_otp_send_code(cls, notification, phone_number):
        pattern = ''  # TODO: Add your pattern code here later
        send_sms(phone_number, pattern, {
            'code': notification.kwargs['code']
        })

    @classmethod
    def handler_login_success(cls, notification, phone_number):
        pattern = ''  # TODO: Add your pattern code here later
        send_sms(phone_number, pattern, {
            'user': notification.to_user.get_full_name(),
            'ip': notification.kwargs['ip'],
        })

    @classmethod
    def handler_register_success(cls, notification, phone_number):
        pattern = ''  # TODO: Add your pattern code here later
        send_sms(phone_number, pattern, {
            'user': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_reset_password_code_sent(cls, notification, phone_number):
        pattern = ''  # TODO: Add your pattern code here later
        send_sms(phone_number, pattern, {
            'code': notification.kwargs['code']
        })

    @classmethod
    def handler_reset_password_successfully(cls, notification, phone_number):
        pattern = ''  # TODO: Add your pattern code here later
        send_sms(phone_number, pattern, {
            'user': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_confirm_phone_number_send_code(cls, notification, phone_number):
        pattern = ''  # TODO: Add your pattern code here later
        send_sms(phone_number, pattern, {
            'code': notification.kwargs['code']
        })

    @classmethod
    def handler_confirm_phone_number_successfully(cls, notification, phone_number):
        pattern = ''  # TODO: Add your pattern code here later
        send_sms(phone_number, pattern, {
            'user': notification.to_user.get_full_name()
        })


SMS_NOTIFICATION_HANDLERS = {
    'OTP_SEND_CODE': NotificationUser.handler_otp_send_code,
    'LOGIN_SUCCESS': NotificationUser.handler_login_success,
    'REGISTER_SUCCESS': NotificationUser.handler_register_success,
    'RESET_PASSWORD_SEND_CODE': NotificationUser.handler_reset_password_code_sent,
    'RESET_PASSWORD_SUCCESSFULLY': NotificationUser.handler_reset_password_successfully,
    'CONFIRM_PHONENUMBER_SEND_CODE': NotificationUser.handler_confirm_phone_number_send_code,
    'CONFIRM_PHONENUMBER_SUCCESSFULLY': NotificationUser.handler_confirm_phone_number_successfully,
}
