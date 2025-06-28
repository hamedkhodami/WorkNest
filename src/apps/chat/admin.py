from django.contrib import admin
from .models import ChatRoomModel, MessageModel


class MessageInline(admin.TabularInline):
    model = MessageModel
    extra = 0
    fields = ("sender", "content", "is_read", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(ChatRoomModel)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "participant_names", "created_at")
    search_fields = ("participants__first_name", "participants__last_name", "participants__phone_number")
    inlines = [MessageInline]

    def participant_names(self, obj):
        return ", ".join([p.full_name() for p in obj.participants.all()])
    participant_names.short_description = "Participants"


@admin.register(MessageModel)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender", "short_content", "is_read", "created_at")
    list_filter = ("is_read", "sender")
    search_fields = ("content", "sender__first_name", "sender__last_name", "room__id")
    readonly_fields = ("created_at",)

    def short_content(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    short_content.short_description = "Message"