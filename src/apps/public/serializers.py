from rest_framework import serializers

from apps.account.models import User
from apps.team.models import TeamModel


class ViewerUserSerializer(serializers.ModelSerializer):
    """
        serializer for public teams with role viewer
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'full_name',
            'phone_number',
            'email',
        ]

    def get_full_name(self, obj):
        return obj.full_name()


class ViewerUserResponseSerializer(serializers.Serializer):
    """
        serializer response for user with role viewer
    """
    data = ViewerUserSerializer(many=True)


class PublicTeamSerializer(serializers.ModelSerializer):
    """
        serializer for public teams
    """
    visibility = serializers.SerializerMethodField()

    class Meta:
        model = TeamModel
        fields = [
            'name',
            'created_by',
            'description',
            'is_public',
            'visibility',
        ]

    def get_visibility(self, obj):
        return "Public" if obj.is_public else "Private"


class PublicTeamSerializerResponseSerializer(serializers.Serializer):
    """
        serializer response for public teams
    """
    data = PublicTeamSerializer(many=True)
