from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models, text, enums

STATUS_CHOICES = enums.JoinTeamStatusEnum


@admin.register(models.TeamModel)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'member_count', 'is_team_public', 'is_locked', 'is_public')
    list_filter = ('is_public', 'is_locked')
    search_fields = ('name',)
    ordering = ('-created_by',)

    actions = ['lock_teams', 'unlock_teams']

    def lock_teams(self, request, queryset):
        queryset.update(is_locked=True)
        self.message_user(request, text.teams_locked)

    def unlock_teams(self, request, queryset):
        queryset.update(is_locked=False)
        self.message_user(request, text.teams_opened)

    lock_teams.short_description = text.lock_team
    unlock_teams.short_description = text.open_team


@admin.register(models.TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'responsible')
    list_filter = ('team',)
    search_fields = ('user__full_name', 'team__name')
    ordering = ('team', 'user')

    actions = ['remove_members']

    def remove_members(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, _(f"{count} Team members were removed"))

    remove_members.short_description = text.remove_member


@admin.register(models.TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('inviter', 'invitee', 'team', 'status', 'created_at')
    list_filter = ('status', 'team')
    search_fields = ('inviter__full_name', 'invitee__username', 'team__name')
    ordering = ('-created_at',)

    actions = ['accept_invites', 'reject_invites']

    def accept_invites(self, request, queryset):
        count = queryset.filter(status=STATUS_CHOICES.PENDING).update(status=STATUS_CHOICES.ACCEPTED)
        self.message_user(request, _(f"{count} Invitation accepted"))

    def reject_invites(self, request, queryset):
        count = queryset.filter(status=STATUS_CHOICES.PENDING).update(status=STATUS_CHOICES.REJECTED)
        self.message_user(request, _(f"{count} Invitation Rejected "))

    accept_invites.short_description = text.accept_invitations
    reject_invites.short_description = text.reject_invitations


@admin.register(models.TeamJoinRequest)
class TeamJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'status', 'resolved_by')
    list_filter = ('status', 'team')
    search_fields = ('user__full_name', 'team__name')
    ordering = ('-id',)

    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        count = queryset.filter(status=STATUS_CHOICES.PENDING).update(status=STATUS_CHOICES.ACCEPTED)
        self.message_user(request, f"{count} Invitation accepted")

    def reject_requests(self, request, queryset):
        count = queryset.filter(status=STATUS_CHOICES.PENDING).update(status=STATUS_CHOICES.REJECTED)
        self.message_user(request, f"{count} Invitation Rejected ")

    approve_requests.short_description = text.accept_invitations
    reject_requests.short_description = text.reject_invitations

