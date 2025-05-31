from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from . import models, text, exceptions, enums
from apps.account.enums import UserRoleEnum


User = get_user_model()
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

        if not request_user.is_authenticated or not request_user.is_active:
            raise exceptions.PermissionDenied

        try:
            team = models.TeamModel.objects.create(**validated_data)
        except Exception as e:
            raise exceptions.NotCreateTeam

        models.TeamMembership.objects.create(user=request_user, team=team, responsible=_('Owner'))

        request_user.role = Role.PROJECT_ADMIN
        request_user.save()

        return team


class TeamCreateSerializersResponse(serializers.ModelSerializer):
    """
        team creation response
    """
    class Meta:
        model = models.TeamModel
        fields = ['name', 'description']


