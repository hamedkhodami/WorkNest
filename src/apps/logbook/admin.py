from django.contrib import admin
from .models import LogEntryModel


@admin.register(LogEntryModel)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("event", "actor_display", "team", "board", "target_repr", "short_created_at")
    list_filter = ("event", "team", "board")
    search_fields = ("actor__first_name", "actor__last_name", "target_repr", "extra_data")
    readonly_fields = (
    "created_at", "updated_at", "event", "actor", "team", "board", "target_id", "target_repr", "extra_data")
    ordering = ("-created_at",)
    list_per_page = 30

    def actor_display(self, obj):
        return obj.actor.full_name() if obj.actor else "System"

    actor_display.short_description = "Actor"

    def short_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    short_created_at.short_description = "Created at"


from django.contrib import admin

# Register your models here.
