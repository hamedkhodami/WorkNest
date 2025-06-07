from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from . import models, text, exceptions, enums
from apps.account.enums import UserRoleEnum


STATUS_CHOICES = enums.JoinTeamStatusEnum
Role = UserRoleEnum


class TeamCreateSerializers(serializers.ModelSerializer):
    """
        team creation
    """
    class Meta:
        model = models.TeamModel
        fields = ['name', 'description', 'is_public']

    def validate_name(self, value):
        if models.TeamModel.objects.filter(name=value).exists():
            raise serializers.ValidationError(text.team_registered)
        return value

    def create(self, validated_data):
        request_user = self.context['request'].user
        validated_data['created_by'] = request_user

        try:
            team = models.TeamModel.objects.create(**validated_data)
        except Exception:
            raise exceptions.NotCreateTeam

        return team


class TeamCreateSerializersResponse(serializers.ModelSerializer):
    """
        team creation response
    """
    class Meta:
        model = models.TeamModel
        fields = ['name', 'description', 'created_by']


class UsersSerializers(serializers.Serializer):
    """
        Serializer to display the teams the user is a member of
    """

    teams = serializers.SerializerMethodField()

    def get_teams(self, obj):
        user = self.context['request'].user
        memberships = models.TeamMembership.objects.filter(user=user).select_related('team')
        return [
            {"team_id": membership.team.id, "team_name": membership.team.name}
            for membership in memberships
        ] if memberships.exists() else []


class DetailTeamSerializers(serializers.ModelSerializer):
    """
        serializers detail team
    """

    member_count = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = models.TeamModel
        fields = ['id', 'name', 'description', 'is_public', 'is_locked', 'member_count', 'members']

    def get_member_count(self, obj):
        return obj.member_count()

    def get_members(self, obj):
        return [
            {"user_id": membership.user.id, "user_name": membership.user.full_name()}
            for membership in obj.membership.select_related('user')
        ]


class TeamUpdateSerializers(serializers.ModelSerializer):
    """
        update team
    """
    class Meta:
        model = models.TeamModel
        fields = '__all__'

        def validate_name(self, value):
            if models.TeamModel.objects.filter(name=value).exists():
                raise serializers.ValidationError(text.team_registered)
            return value


class TeamUpdateResponseSerializers(serializers.Serializer):
    """
        update team response
    """
    message = serializers.CharField()
    update_data = TeamUpdateSerializers()


class RequestJoinTeamSerializers(serializers.ModelSerializer):
    """
        serializer join team request
    """
    class Meta:
        model = models.TeamJoinRequest
        fields = ['team', 'user']

    def validated_team(self, value):
        if value.is_locked == True:
            raise serializers.ValidationError(text.team_locked)
        return value

    def validate(self, data):
        user = data["user"]
        team = data["team"]

        if models.TeamJoinRequest.objects.filter(user=user, team=team, status=enums.JoinTeamStatusEnum.PENDING).exists():
            raise serializers.ValidationError(text.team_request_pending)

        return data


class RequestJoinTeamResponseSerializers(serializers.Serializer):
    """Join team request response"""
    message = serializers.CharField()


class ResultJoinTeamSerializers(serializers.ModelSerializer):
    """ Serializer for resolving join requests (Accept/Reject) """

    status = serializers.ChoiceField(choices=STATUS_CHOICES.choices)

    class Meta:
        model = models.TeamJoinRequest
        fields = ['status']

    def validate_status(self, value):
        if value not in [STATUS_CHOICES.ACCEPTED, STATUS_CHOICES.REJECTED]:
            raise serializers.ValidationError(text.invalid_status)
        return value


class TeamInvitationRequestSerializers(serializers.ModelSerializer):
    """
        Serializers Invitation join team for users
    """
    inviter = serializers.StringRelatedField(read_only=True)
    invitee = serializers.StringRelatedField()
    team = serializers.StringRelatedField(read_only=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES.choices)

    class Meta:
        model = models.TeamInvitation
        fields = ['id', 'inviter', 'invitee', 'team', 'status', 'created_at']
        read_only_fields = ['inviter', 'team', 'created_at']

    def validated_team(self, value):
        if value.is_locked == True:
            raise serializers.ValidationError(text.team_locked)
        return value

    def validate_invitee(self, value):
        team = self.initial_data.get("team")
        if models.TeamInvitation.objects.filter(invitee=value, team=team).exists():
            raise serializers.ValidationError(text.duplicate_invitation)
        return value

    def update(self, instance, validated_data):
        if instance.status != validated_data.get('status', instance.status):
            instance.status = validated_data['status']
            instance.save()
        return instance


class TeamInvitationRequestResponseSerializers(serializers.Serializer):
    """
        Serializers Response Invitation join team for users
    """
    message = serializers.CharField()


class UserTeamRequestSerializer(serializers.Serializer):
    """
        Manage membership requests and invitations in a single serializer
    """

    type = serializers.CharField()
    user = serializers.StringRelatedField()
    team = serializers.StringRelatedField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES.choices)
    resolved_by = serializers.StringRelatedField(required=False)

    def to_representation(self, instance):
        if isinstance(instance, models.TeamInvitation):
            return {
                "type": "INVITATION",
                "user": instance.invitee.full_name(),
                "team": instance.team.name,
                "status": instance.status,
                "resolved_by": instance.inviter.full_name()
            }
        elif isinstance(instance, models.TeamJoinRequest):
            return {
                "type": "JOIN_REQUEST",
                "user": instance.user.full_name(),
                "team": instance.team.name,
                "status": instance.status,
                "resolved_by": instance.resolved_by.full_name() if instance.resolved_by else None
            }
        return super().to_representation(instance)









