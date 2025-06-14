from rest_framework import serializers


from apps.core import text

from . import exceptions
from .models import BoardModel


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class CreateBoardSerializer(serializers.ModelSerializer):
    """
      create new board serializers
    """
    class Meta:
        model = BoardModel
        fields = ['title', 'description']

    def create(self, validated_data):
        request_user = self.context['request'].user

        team = getattr(request_user, 'team', None)
        if not team:
            raise serializers.ValidationError(text.not_found)

        validated_data['created_by'] = request_user
        validated_data['team'] = team

        try:
            board = BoardModel.objects.create(**validated_data)
        except Exception:
            raise exceptions.NotCreateBoard

        return board


class CreateBoardSerializerResponse(serializers.ModelSerializer):
    """
      create new board serializers response
    """

    class Meta:
        model = BoardModel
        fields = ['title', 'description', 'created_by', 'team']


class BoardListSerializer(serializers.ModelSerializer):
    """
     list of team boards serializers
    """
    uuid = serializers.UUIDField(source='id', read_only=True)
    team_uuid = serializers.UUIDField(source='team.id', read_only=True)

    class Meta:
        model = BoardModel
        fields = ['uuid', 'title', 'description', 'is_archived', 'team_uuid', 'created_by']


class DetailBoardSerializers(serializers.ModelSerializer):
    """
        serializers detail board
    """

    team = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = BoardModel
        fields = ['title', 'description', 'team', 'created_by']

    def get_created_by(self, obj):
        return {
            "name": obj.created_by.full_name(),
        }

    def get_team(self, obj):
        return {
            "name": obj.team.name,
        }


class BoardDeleteSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    team_id = serializers.UUIDField()

    def validate(self, attrs):
        board_id = attrs.get("id")
        team_id = attrs.get("team_id")
        user = self.context["request"].user

        board = BoardModel.objects.filter(id=board_id, team_id=team_id).first()
        if not board:
            raise serializers.ValidationError({"detail": text.not_match})

        if not hasattr(user, "team") or not user.team or user.team.id != team_id:
            raise serializers.ValidationError({"detail": text.permission_denied})

        attrs["board"] = board
        return attrs


class BoardUpdateSerializers(serializers.ModelSerializer):
    """
        update board serializers
    """
    class Meta:
        model = BoardModel
        fields = '__all__'
        read_only_fields = ("team", "created_by")


class BoardUpdateSerializersResponse(serializers.Serializer):
    """
        update serializers response
    """
    message = serializers.CharField()
    update_date = BoardUpdateSerializers()

