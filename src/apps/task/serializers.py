from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from apps.core import text
from apps.board.models import BoardModel
from . import models, enums


Priority = enums.TaskPriorityEnum
User = get_user_model()


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


class TaskListDeleteSerializer(serializers.Serializer):
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


class TaskListDetailSerializer(serializers.ModelSerializer):
    """
        detail tasklist serializers
    """
    class Meta:
        model = models.TaskListModel
        fields = ['title', 'description', 'order']


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
        serializers to update task
    """
    class Meta:
        model = models.TaskModel
        fields = '__all__'
        read_only_fields = ("task_list", "assignee")


class TaskUpdateResponseSerializers(serializers.ModelSerializer):
    """
        serializer response to update task
    """
    message = serializers.CharField()
    update_date = TaskUpdateSerializer()


class TaskDetailSerializer(serializers.ModelSerializer):
    """
        detail task serializers
    """
    task_list = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskModel
        fields = ['title', 'description', 'is_done', 'deadline', 'priority', 'task_list', 'assignee']

    def get_task_list(self, obj):
        return {"name": obj.task_list.title}

    def get_assignee(self, obj):
        return {"name": obj.assignee.full_name() if obj.assignee else None}


class AdminCreateTaskSerializer(serializers.ModelSerializer):
    """
    ادمین برای یک کاربر وظیفه جدید می‌سازد و آن را به یک لیست مرتبط می‌کند.
    """
    assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    task_list = serializers.PrimaryKeyRelatedField(queryset=models.TaskListModel.objects.all())

    class Meta:
        model = models.TaskModel
        fields = [
            'title',
            'description',
            'deadline',
            'priority',
            'task_list',
            'assignee'
        ]


class RemoveTaskSerializer(serializers.Serializer):
    """
       serializers remove user from tasklist
    """
    id = serializers.UUIDField()
    task_list_id = serializers.UUIDField()

    def validate(self, attrs):
        task_id = attrs.get('id')
        task_list_id = attrs.get('task_list_id')

        task = get_object_or_404(models.TaskModel, id=task_id, task_list_id=task_list_id)

        if not task:
            raise serializers.ValidationError({'detail': text.not_match})

        attrs['task'] = task
        return attrs


