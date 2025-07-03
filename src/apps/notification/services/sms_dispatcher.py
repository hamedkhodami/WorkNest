from apps.notification.sms import SMS_NOTIFICATION_HANDLERS


def dispatch_sms_notification(notification):
    """
    Finds and executes the corresponding SMS handler based on notification.kwargs['type'].
    """
    notif_type = notification.kwargs.get('type')

    if not notif_type:
        raise ValueError("Missing 'type' in notification kwargs for SMS dispatch.")

    handler = SMS_NOTIFICATION_HANDLERS.get(notif_type)
    if not handler:
        raise ValueError(f"No SMS handler found for notification type '{notif_type}'.")

    phone_number = notification.phone_number
    if not phone_number:
        raise ValueError("Notification does not have a phone number to send SMS.")

    handler(notification, phone_number)
