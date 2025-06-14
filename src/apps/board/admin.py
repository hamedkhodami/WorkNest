from django.contrib import admin

from apps.core import text
from .models import BoardModel


@admin.register(BoardModel)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'is_archived', 'team', 'created_by')
    list_filter = ('is_archived', )
    search_fields = ('title',)

    actions = ['archive_board', 'restore_board']

    def archive_board(self, request, queryset):
        queryset.update(is_archived=True)
        self.message_user(request, text.archive_board)

    def restore_board(self, request, queryset):
        queryset.update(is_archived=False)
        self.message_user(request, text.restore_board)

    archive_board.short_description = text.lock_team
    restore_board.short_description = text.open_team

