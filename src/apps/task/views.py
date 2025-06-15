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
