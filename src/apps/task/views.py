from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions as base_permissions

from apps.core.views import mixins
from apps.core.swagger import mixins as ms
from apps.core import text
from apps.core.services.access_control import is_team_member
from apps.account.auth import permissions as per
from apps.team.models import TeamModel
from apps.board.models import BoardModel

from . import models, exceptions, serializers, enums


class TaskCreationView(ms.SwaggerViewMixin, mixins.CreateViewMixin, APIView):
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

    serializer_response = serializers.TaskDeleteSerializer

    def delete(self, request, *args, **kwargs):
        return self.delete_instance(request)

    def get_instance(self):
        ser = self.serializer_response(data=self.request.data, context={'request':self.request})
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


