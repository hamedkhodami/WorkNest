from apps.notification.email import EMAIL_NOTIFICATION_HANDLERS


def dispatch_email_notification(notification):
    """
    Finds and executes the corresponding email handler based on notification.kwargs['type'].
    """
    notif_type = notification.kwargs.get('type')

    if not notif_type:
        raise ValueError("Missing 'type' in notification kwargs for email dispatch.")

    handler = EMAIL_NOTIFICATION_HANDLERS.get(notif_type)
    if not handler:
        raise ValueError(f"No handler found for email notification type '{notif_type}'.")

    handler(notification, notification.email)
