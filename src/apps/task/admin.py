from django.contrib import admin
from . import models


@admin.register(models.TaskListModel)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'order', 'description_summary']
    list_filter = ['board__team']
    search_fields = ['title', 'description']
    ordering = ['board', 'order']

    def description_summary(self, obj):
        return (obj.description[:50] + "...") if obj.description else "-"
    description_summary.short_description = "Description"


@admin.register(models.TaskModel)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_list', 'assignee', 'is_done', 'deadline', 'priority']
    list_filter = ['is_done', 'priority', 'task_list__board__team']
    search_fields = ['title', 'description', 'assignee__full_name']
    list_editable = ['is_done', 'priority']
    date_hierarchy = 'deadline'

