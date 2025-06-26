from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.task.models import TaskModel

from . import enums, models


@receiver(post_save, sender=TaskModel)
def log_task_save(sender, instance, created, **kwargs):
    board = getattr(getattr(instance, "task_list", None), "board", None)
    team = getattr(board, "team", None)

    if not team or not board:
        return

    event = enums.LogEventEnum.TASK_CREATE if created else enums.LogEventEnum.TASK_UPDATE

    models.LogEntryModel.objects.create(
        event=event,
        actor=None,
        team=team,
        board=board,
        target_id=instance.id,
        target_repr=instance.title,
        extra_data={"list_id": str(instance.task_list.id)} if instance.task_list else None,
    )
