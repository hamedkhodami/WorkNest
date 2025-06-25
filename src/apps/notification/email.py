from .tasks import send_email


class EmailNotificationHandler:

    @classmethod
    def project_report_handler(cls, email_notification, recipient_email):
        subject = "Your Project Report"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "project_name": email_notification.kwargs.get('project_name'),
            "report_link": email_notification.kwargs.get('report_link'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def team_invitation_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "team_name": email_notification.kwargs.get('team_name'),
            "invitation_link": email_notification.kwargs.get('invitation_link'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def board_creation_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "board_name": email_notification.kwargs.get('board_name'),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def add_task_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "task_title": email_notification.kwargs.get('task_title'),
            "board_title": email_notification.kwargs.get('board_title'),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)


EMAIL_NOTIFICATION_HANDLERS = {
    'PROJECT_REPORT': EmailNotificationHandler.project_report_handler,
    'TEAM_INVITATION': EmailNotificationHandler.team_invitation_handler,
    'BOARD_CREATION': EmailNotificationHandler.board_creation_handler,
    'ADDED_TASK': EmailNotificationHandler.add_task_handler,

}
