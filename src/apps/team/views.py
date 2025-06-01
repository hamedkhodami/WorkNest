from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions as base_permissions

from drf_yasg.utils import swagger_auto_schema

from apps.core.views import mixins
from apps.core.swagger import mixins as ms

from . import models, exceptions, serializers


User = get_user_model()


class TeamCreateView(ms.SwaggerViewMixin, APIView):
    """
        team creation view
    """
    swagger_title = 'Team creation'
    swagger_tags = ['Team']
    serializer = serializers.TeamCreateSerializers
    serializer_response = serializers.TeamCreateSerializersResponse
    permission_classes = [base_permissions.IsAuthenticated]

    def post(self, request):
        ser = self.serializer(data=request.data, context={"request": request})

        if ser.is_valid():
            team = ser.save()
            if not ser.is_valid():
                raise exceptions.NotCreateTeam
            response_ser = self.serializer_response(team)
            return Response(response_ser.data, status=status.HTTP_201_CREATED)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersTeamsView(ms.SwaggerViewMixin, APIView):
    """
        view to display the teams the user is a member of
    """
    swagger_title = 'Users Team'
    swagger_tags = ['Team']
    serializer_class = serializers.UsersSerializers
    permission_classes = [base_permissions.IsAuthenticated]

    def get(self, request):
        serializer = self.serializer_class(instance=request.user, context={"request": request})
        return Response(serializer.data, status=200)





