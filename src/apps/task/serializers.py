from rest_framework import serializers
from django.shortcuts import get_object_or_404
import uuid

from apps.core import text
from apps.board.models import BoardModel
from . import models, exceptions, enums


Priority = enums.TaskPriorityEnum


class TaskListCreateSerializer(serializers.ModelSerializer):
    """
       serializers create list task
    """
    class Meta:
        model = models.TaskListModel
        fields = ['title', 'description', 'order']

    def create(self, validated_data):
        team_id = self.context['request'].data.get("team_id")
        board = get_object_or_404(BoardModel, team_id=team_id)
        last_task_list = models.TaskListModel.objects.filter(board=board).order_by("-order").first()
        validated_data['order'] = (last_task_list.order + 1) if last_task_list else 1
        validated_data['board'] = board
        return super().create(validated_data)


class TaskListCreateSerializersResponse(serializers.ModelSerializer):
    """
       response serializers create list task
    """
    board_title = serializers.CharField(source="board.title", read_only=True)

    class Meta:
        model = models.TaskListModel
        fields = ['title', 'description', 'board_title']


class TaskDeleteSerializer(serializers.Serializer):
    """
        serializer delete task
    """
    id = serializers.UUIDField()
    board_id = serializers.UUIDField()

    def validate(self, attrs):
        tasklist_id = attrs.get('id')
        board_id = attrs.get('board_id')

        tasklist = get_object_or_404(models.TaskListModel, id=tasklist_id, board_id=board_id)

        if not tasklist:
            raise serializers.ValidationError({'detail': text.not_match})

        if not tasklist.board:
            raise serializers.ValidationError({'detail': text.tasklist_not_board})

        attrs['tasklist'] = tasklist
        return attrs


class TaskListsSerializer(serializers.ModelSerializer):
    """
     serializers list of all tasklist
    """
    id = serializers.UUIDField(read_only=True)
    board_uuid = serializers.UUIDField(source="board.id", read_only=True)
    title = serializers.CharField(read_only=True)

    class Meta:
        model = models.TaskListModel
        fields = ['id', 'board_uuid', 'title']

