from .tasks import send_email


class EmailTeamNotificationHandler:

    @classmethod
    def team_creation_handler(cls, email_notification, recipient_email):
        subject = "You're Created Team"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def team_request_join_handler(cls, email_notification, recipient_email):
        subject = "You Have a Request to Join a Team"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "team_name": email_notification.kwargs.get('team_name'),
            "invitation_link": email_notification.kwargs.get('invitation_link'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def team_result_join_handler(cls, email_notification, recipient_email):
        subject = "Result Join a Team"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "team_name": email_notification.kwargs.get('team_name'),
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
    def team_result_invitation_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def team_remove_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)


class EmailTaskNotificationHandler:

    @classmethod
    def add_task_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "user_name": email_notification.to_user.get_full_name(),
            "task_title": email_notification.kwargs.get('task_title'),
            "board_title": email_notification.kwargs.get('board_title'),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def remove_task_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "task_title": email_notification.kwargs.get('task_title'),
            "user_name": email_notification.to_user.get_full_name(),
            "board_title": email_notification.kwargs.get('board_title'),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)

    @classmethod
    def update_task_handler(cls, email_notification, recipient_email):
        subject = "You're Invited to Join a Team"
        context = {
            "task_title": email_notification.kwargs.get('task_title'),
            "user_name": email_notification.to_user.get_full_name(),
            "board_title": email_notification.kwargs.get('board_title'),
            "team_name": email_notification.kwargs.get('team_name'),
        }
        send_email(subject, [recipient_email], context)


EMAIL_NOTIFICATION_HANDLERS = {

    # team
    'TEAM_CREATION': EmailTeamNotificationHandler.team_creation_handler,
    'TEAM_JOIN': EmailTeamNotificationHandler.team_request_join_handler,
    'TEAM_RESULT_JOIN': EmailTeamNotificationHandler.team_result_join_handler,
    'TEAM_INVITATION': EmailTeamNotificationHandler.team_invitation_handler,
    'TEAM_RESULT_INVITATION': EmailTeamNotificationHandler.team_result_invitation_handler,
    'TEAM_REMOVE': EmailTeamNotificationHandler.team_remove_handler,

    # task
    'ADDED_TASK': EmailTaskNotificationHandler.add_task_handler,
    'REMOVED_TASK': EmailTaskNotificationHandler.remove_task_handler,
    'UPDATED_TASK': EmailTaskNotificationHandler.update_task_handler,

}
