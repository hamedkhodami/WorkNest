from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.board.models import BoardModel

from . import enums

Priority = enums.TaskPriorityEnum


class TaskListModel(BaseModel):
    board = models.ForeignKey(BoardModel, verbose_name=_('Board'), on_delete=models.SET_NULL, null=True)
    title = models.CharField(_('Title'), max_length=128)
    description = models.TextField(_('Description'), blank=True, null=True)
    order = models.PositiveIntegerField(_('Order'), default=0, db_index=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("TaskList")
        verbose_name_plural = _("TaskLists")
        constraints = [
            models.UniqueConstraint(fields=['board', 'order'], name='unique_tasklist_order')
        ]

    def __str__(self):
        return f"{self.board.title} - {self.title}"

    def get_tasks(self):
        return self.tasks.all()


class TaskModel(BaseModel):
    task_list = models.ForeignKey(TaskListModel, verbose_name=_('Task list'),
                                  on_delete=models.CASCADE, related_name='tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Assignee'), on_delete=models.SET_NULL,
                                 null=True, related_name='assigned_tasks')
    title = models.CharField(_('Title'), max_length=128)
    description = models.TextField(_('Description'), blank=True, null=True)
    is_done = models.BooleanField(_('Is done'), default=False)
    deadline = models.DateTimeField(_('Deadline'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completed at'), null=True, blank=True)
    priority = models.CharField(_('Priority'), choices=Priority, default=Priority.MEDIUM)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    def __str__(self):
        return self.title

    def mark_as_done(self):
        self.is_done = True
        self.completed_at = now()
        self.save()

    def is_overdue(self):
        return self.deadline and self.deadline < now() and not self.is_done

