from django.contrib import admin
from apps.notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'status', 'title', 'user', 'email',
        'phone_number', 'is_visited', 'retry_count', 'sent_at', 'created_at'
    )
    list_filter = ('type', 'status', 'is_visited', 'created_at')
    search_fields = ('title', 'description', 'email', 'phone_number')
    readonly_fields = ('retry_count', 'sent_at', 'created_at')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'type', 'status', 'title', 'description', 'kwargs'
            )
        }),
        ('Recipient', {
            'fields': ('user', 'email', 'phone_number')
        }),
        ('Status & Meta', {
            'fields': ('is_visited', 'retry_count', 'sent_at', 'created_at')
        }),
    )