from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.views import mixins
from apps.core.swagger import mixins as ms
from apps.core import text
from apps.core.services.access_control import is_team_member
from apps.account.auth import permissions as per
from apps.team.models import TeamModel
from apps.board.models import BoardModel

from . import models, exceptions, serializers


class TaskListCreationView(ms.SwaggerViewMixin, mixins.CreateViewMixin, APIView):
    """
       view create list task
    """
    swagger_title = 'Task creation'
    swagger_tags = ['Task']
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer = serializers.TaskListCreateSerializer
    serializer_response = serializers.TaskListCreateSerializersResponse

    def post(self, request, *args, **kwargs):
        team_id = request.data.get("team_id")

        if not team_id:
            raise exceptions.NotFoundTeam()

        team = TeamModel.objects.filter(id=team_id).first()
        is_team_member(request.user, team)

        response_data = self.create(request, response=False, *args, **kwargs)
        return Response(response_data, status=status.HTTP_201_CREATED)


class TaskListDeleteView(ms.SwaggerViewMixin, mixins.DeleteViewMixin, APIView):
    """
        view delete task
    """

    swagger_title = "Task delete"
    swagger_tags = ["Task"]
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer_response = serializers.TaskListDeleteSerializer

    def delete(self, request, *args, **kwargs):
        return self.delete_instance(request)

    def get_instance(self):
        ser = self.serializer_response(data=self.request.data, context={'request': self.request})
        ser.is_valid(raise_exception=True)
        self.validated_data = ser.validated_data
        tasklist = self.validated_data['tasklist']

        is_team_member(self.request.user, tasklist.board.team)
        return tasklist


class TaskListsView(ms.SwaggerViewMixin, mixins.ListViewMixin, APIView):
    """
        View to list all task lists
    """
    swagger_title = "Task Lists"
    swagger_tags = ["Task"]
    permission_classes = (per.IsTeamUser,)
    serializer_response = serializers.TaskListsSerializer

    def get_queryset(self):
        board_id = self.request.query_params.get("board_id")
        queryset = models.TaskListModel.objects.all()

        if board_id:
            board = get_object_or_404(BoardModel, id=board_id)
            is_team_member(self.request.user, board.team)
            queryset = queryset.filter(board=board)

        return queryset.order_by("id")

    def get(self, request, *args, **kwargs):
        response_data = self.list(request)

        if isinstance(response_data, Response):
            return response_data

        return Response({"data": response_data}, status=status.HTTP_200_OK)


# TODO: complete test
class TaskListsDetailView(ms.SwaggerViewMixin, mixins.DetailViewMixin, APIView):
    """
        View to list detail task lists
    """
    swagger_title = "TaskList Detail"
    swagger_tags = ["Task"]
    permission_classes = (per.IsTeamUser,)
    serializer_response = serializers.TaskListDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.detail(request)

    def get_instance(self):
        tasklist_id = self.kwargs.get('tasklist_id')
        tasklist = models.TaskListModel.objects.filter(id=tasklist_id).first()
        if not tasklist:
            raise exceptions.NotFound()

        is_team_member(self.request.user, tasklist.board.team)

        return tasklist


class AddTaskToUserView(ms.SwaggerViewMixin, mixins.CreateViewMixin, APIView):
    """
    Assign an existing task to a user (by admin or project admin)
    """
    swagger_title = "Assign Task to User"
    swagger_tags = ["Task"]
    permission_classes = (per.IsAdminOrProjectAdmin,)
    serializer = serializers.AdminCreateTaskSerializer
    serializer_response = serializers.TaskDetailSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request)

    def before_save(self):
        task_list = self.validated_data["task_list"]
        assignee = self.validated_data["assignee"]

        is_team_member(self.request.user, task_list.board.team)
        is_team_member(assignee, task_list.board.team)


class RemoveTaskView(ms.SwaggerViewMixin, mixins.DeleteViewMixin, APIView):
    """
       view remove user from tasklist
    """
    swagger_title = "User Task remove"
    swagger_tags = ["Task"]
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer_response = serializers.RemoveTaskSerializer

    def delete(self, request):
        return self.delete_instance(request)

    def get_instance(self):
        ser = self.serializer_response(data=self.request.data, context={'request': self.request})
        ser.is_valid(raise_exception=True)
        self.validated_data = ser.validated_data
        task = self.validated_data['task']

        is_team_member(self.request.user, task.task_list.board.team)
        return task


class TaskUpdateView(ms.SwaggerViewMixin, mixins.UpdateViewMixin, APIView):
    """
        view to update task
    """
    swagger_title = "TaskList Update"
    swagger_tags = ["Task"]
    permission_classes = (per.IsAdminOrProjectAdmin,)
    serializer = serializers.TaskUpdateSerializer
    serializer_response = serializers.TaskUpdateResponseSerializers

    def get_instance(self):
        task_id = self.kwargs.get('task_id')
        task = models.TaskModel.objects.filter(id=task_id).first()
        if not task:
            raise exceptions.NotFound()

        is_team_member(self.request.user, task.task_list.board.team)

        return task

    def put(self, request, *args, **kwargs):
        instance = self.get_instance()
        ser = self.serializer(instance, data=self.request.data, partial=True, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()

        return Response({
            'message': text.success_update,
            'update_date': ser.data,
        }, status=200)


class TaskDetailView(ms.SwaggerViewMixin, mixins.DetailViewMixin, APIView):
    """
        View to list detail task
    """
    swagger_title = "Task Detail"
    swagger_tags = ["Task"]
    permission_classes = (per.IsTeamUser,)
    serializer_response = serializers.TaskDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.detail(request)

    def get_instance(self):
        task_id = self.kwargs.get('task_id')
        task = models.TaskModel.objects.filter(id=task_id).first()
        if not task:
            raise exceptions.NotFound()

        is_team_member(self.request.user, task.task_list.board.team)

        return task




