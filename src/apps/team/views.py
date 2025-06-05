from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions as base_permissions

from drf_yasg.utils import swagger_auto_schema

from apps.core.views import mixins
from apps.core.swagger import mixins as ms
from apps.account.auth import permissions as per
from . import models, exceptions, serializers, text, enums
from .service.create_membership import create_membership_if_accepted


User = get_user_model()
STATUS_CHOICES = enums.JoinTeamStatusEnum


# TODO: improve by mixins & permission change to viewer
class TeamCreateView(ms.SwaggerViewMixin, APIView):
    """ Team creation view """
    swagger_title = 'Team creation'
    swagger_tags = ['Team']
    serializer = serializers.TeamCreateSerializers
    serializer_response = serializers.TeamCreateSerializersResponse
    permission_classes = [base_permissions.IsAuthenticated]

    def post(self, request):
        ser = self.serializer(data=request.data, context={"request": request})

        if ser.is_valid():
            team = ser.save()
            response_ser = self.serializer_response(team, context={"request": request})
            return Response(response_ser.data, status=status.HTTP_201_CREATED)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO: improve by mixins
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


class TeamDetailView(ms.SwaggerViewMixin, mixins.DetailViewMixin, APIView):
    """
        detail team view
    """
    swagger_title = 'Details Team'
    swagger_tags = ['Team']
    permission_classes = [permissions.IsAuthenticated]
    serializer_response = serializers.DetailTeamSerializers


    def get(self, request, *args, **kwargs):
        return self.detail(request)

    def get_instance(self):
        team_id = self.kwargs.get('team_id')
        team = models.TeamModel.objects.filter(id=team_id).first()
        if not team:
            raise exceptions.NotFoundTeam()
        return team


class TeamUpdateViews(ms.SwaggerViewMixin, mixins.UpdateViewMixin, APIView):
    """
        update team view
    """
    swagger_title = 'Update Team'
    swagger_tags = ['Team']
    permission_classes = (per.IsAdminOrProjectAdmin,)
    serializer = serializers.TeamUpdateSerializers
    serializer_response = serializers.TeamUpdateResponseSerializers

    def get_instance(self):
        team_id = self.kwargs.get('team_id')
        team = models.TeamModel.objects.filter(id=team_id).first()

        if not team:
            raise exceptions.NotFoundTeam

        self.check_permissions(self.request)

        return team

    def put(self, request, *args, **kwargs):

        instance = self.get_instance()
        ser = self.serializer(instance, data=request.data, partial=True, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()

        return Response({
            "message": text.success_team_update,
            "updated_data": ser.data
        }, status=200)


# TODO: permission change to viewer
class JoinTeamView(ms.SwaggerViewMixin, APIView):
    """
        view join team request
    """
    swagger_title = 'Request join'
    swagger_tags = ['Team']
    serializer = serializers.RequestJoinTeamSerializers
    serializer_response = serializers.RequestJoinTeamResponseSerializers
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        team = ser.validated_data["team"]
        if team.is_locked:
            return Response({"message": text.team_locked}, status=status.HTTP_403_FORBIDDEN)

        ser.save()

        response_serializer = self.serializer_response({
            "message": text.success_team_request,
        })
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ResultJoinTeamView(ms.SwaggerViewMixin, APIView):
    """
        View for resolving join requests (Accept/Reject)
    """
    swagger_title = 'Result join'
    swagger_tags = ['Team']
    serializer = serializers.ResultJoinTeamSerializers
    permission_classes = (per.IsAdminOrProjectAdmin,)
    accept_request = create_membership_if_accepted


    def post(self, request, pk):
        accept_request = create_membership_if_accepted
        join_request = get_object_or_404(models.TeamJoinRequest, pk=pk)
        ser = self.serializer(join_request, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        accept_request(join_request)

        # TODO: Implement notification system

        return Response({"message": text.request_resolved}, status=status.HTTP_200_OK)



