from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions as base_permissions

from apps.core.views import mixins
from apps.core.swagger import mixins as ms

from apps.account.models import User
from apps.account.enums import UserRoleEnum
from apps.team.models import TeamModel

from . import serializers


class ViewerUserView(ms.SwaggerViewMixin, mixins.ListViewMixin, APIView):
    """
        view for user with role viewer
    """
    swagger_title = 'User Viewer List'
    swagger_tags = ['Public']
    permission_classes = (base_permissions.AllowAny,)
    serializer_response = serializers.ViewerUserResponseSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role=UserRoleEnum.VIEWER).order_by('?')[:10]
        return queryset

    def get(self, request, *args, **kwargs):
        response_data = self.list(request)

        if isinstance(response_data, Response):
            return response_data

        return Response({"data": response_data}, status=status.HTTP_200_OK)


class PublicTeamView(ms.SwaggerViewMixin, mixins.ListViewMixin, APIView):
    """
        view for user with role viewer
    """
    swagger_title = 'Public team List'
    swagger_tags = ['Public']
    permission_classes = (base_permissions.AllowAny,)
    serializer_response = serializers.PublicTeamSerializerResponseSerializer

    def get_queryset(self):
        queryset = TeamModel.objects.filter(is_public=True).order_by('?')[:10]
        return queryset

    def get(self, request, *args, **kwargs):
        response_data = self.list(request)

        if isinstance(response_data, Response):
            return response_data

        return Response({"data": response_data}, status=status.HTTP_200_OK)