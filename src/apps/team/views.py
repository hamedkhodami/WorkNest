from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.conf import settings
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
from apps.account.models import User
from apps.notification.utils import create_notify
from apps.notification.enums import NotificationType
from apps.notification.services.email_dispatcher import dispatch_email_notification

from . import models, serializers, enums, exceptions
from .service.create_membership import create_membership_if_accepted


STATUS_CHOICES = enums.JoinTeamStatusEnum


class TeamCreateView(ms.SwaggerViewMixin, mixins.CreateViewMixin, APIView):
    """Team creation view"""
    swagger_title = 'Team creation'
    swagger_tags = ['Team']
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer = serializers.TeamCreateSerializers
    serializer_response = serializers.TeamCreateSerializersResponse

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        team = serializer.save(created_by=self.request.user)

        notification = create_notify(
            to_user=self.request.user,
            title=_("Team Created"),
            description=_("A new team '{team.name}' has been created.").format(
                team=team.name
            ),
            kwargs={
                'team_name': team.name,
                'type': 'TEAM_CREATION'
            }
        )

        if notification.type == NotificationType.EMAIL:
            dispatch_email_notification(notification)


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
            raise exceptions.NotFoundTeam()

        is_team_member(self.request.user, team)

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


class JoinTeamView(ms.SwaggerViewMixin, APIView):
    """
        view join team request
    """
    swagger_title = 'Request join'
    swagger_tags = ['Team']
    serializer = serializers.RequestJoinTeamSerializers
    serializer_response = serializers.RequestJoinTeamResponseSerializers
    permission_classes = (per.IsViewer,)

    def post(self, request):
        ser = self.serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        team = ser.validated_data["team"]
        if team.is_locked:
            return Response({"message": text.team_locked}, status=status.HTTP_403_FORBIDDEN)

        ser.save()

        notification = create_notify(
            to_user=self.request.user,
            title=_("Team Join Request"),
            description=_("{user} request to join team '{team}'").format(
                user=request.user.full_name(),
                team=team.name
            ),
            kwargs={
                'team_name': team.name,
                'type': 'TEAM_JOIN'
            }
        )

        if notification.type == NotificationType.EMAIL:
            dispatch_email_notification(notification)

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

    def post(self, request, pk):
        accept_request = create_membership_if_accepted
        join_request = get_object_or_404(models.TeamJoinRequest, pk=pk)
        ser = self.serializer(join_request, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        accept_request(join_request)

        notification = create_notify(
            to_user=join_request.user,
            title=_("Team Join Result"),
            description=_("{user} your request to join team '{team}' has been resolved.").format(
                user=join_request.user.full_name(),
                team=join_request.team.name
            ),
            kwargs={
                'team_name': join_request.team.name,
                'type': 'TEAM_RESULT_JOIN'
            }
        )

        if notification.type == NotificationType.EMAIL:
            dispatch_email_notification(notification)

        return Response({"message": text.request_resolved}, status=status.HTTP_200_OK)


class TeamInvitationRequestView(ms.SwaggerViewMixin, APIView):
    """
        views Invitation join team for users
    """

    swagger_title = 'Result Invite'
    swagger_tags = ['Team']
    serializer = serializers.TeamInvitationRequestSerializers
    serializer_response = serializers.TeamInvitationRequestResponseSerializers
    permission_classes = (per.IsAdminOrProjectAdmin,)

    def post(self, request):
        data = request.data
        inviter = request.user
        team = get_object_or_404(models.TeamModel, pk=data.get("team_id"))
        invitee = get_object_or_404(User, pk=data.get("invitee_id"))

        if team.is_locked:
            return Response({"error": text.team_locked}, status=status.HTTP_400_BAD_REQUEST)

        if models.TeamMembership.objects.filter(user=invitee, team=team).exists():
            return Response({"error": text.already_team_member}, status=status.HTTP_400_BAD_REQUEST)

        if models.TeamInvitation.objects.filter(invitee=invitee, team=team).exists():
            return Response({"error": text.duplicate_invitation}, status=status.HTTP_400_BAD_REQUEST)

        ser = self.serializer(data=data)
        ser.is_valid(raise_exception=True)
        validated_data = ser.validated_data
        validated_data["team"] = team
        validated_data["inviter"] = inviter
        ser.save()

        notification = create_notify(
            to_user=invitee,
            title=_("Team Invitation"),
            description=_("{user} invited you to join team '{team}'").format(
                user=inviter.full_name(),
                team=team.name
            ),
            kwargs={
                'team_name': team.name,
                'invitation_link': f"{settings.FRONTEND_URL}/teams/{team.id}/invitation",
                'type': 'TEAM_INVITATION'
            }
        )

        if notification.type == NotificationType.EMAIL:
            dispatch_email_notification(notification)

        response_serializer = self.serializer_response({"message": text.success_team_request}).data
        return Response(response_serializer, status=status.HTTP_201_CREATED)


class ResultInvitationTeamView(ms.SwaggerViewMixin, APIView):
    """
        View for resolving invitation requests (Accept/Reject)
    """
    swagger_title = 'Result Invitation'
    swagger_tags = ['Team']
    serializer = serializers.ResultJoinTeamSerializers
    permission_classes = (per.IsViewer,)

    def post(self, request, pk):
        join_request = get_object_or_404(models.TeamInvitation, pk=pk)

        if request.user != join_request.invitee:
            return Response({"error": text.permission_denied}, status=status.HTTP_403_FORBIDDEN)

        ser = self.serializer(join_request, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()

        if ser.validated_data.get("status") == STATUS_CHOICES.ACCEPTED:
            models.TeamMembership.objects.get_or_create(user=request.user, team=join_request.team)

        notification = create_notify(
            to_user=join_request.inviter,
            title=_("Invitation Response"),
            description=_("{user} has responded to your invitation for team '{team}'").format(
                user=request.user.full_name(),
                team=join_request.team.name
            ),
            kwargs={
                'team_name': join_request.team.name,
                'type': 'TEAM_RESULT_INVITATION'
            }
        )

        if notification.type == NotificationType.EMAIL:
            dispatch_email_notification(notification)

        return Response({"message": text.request_resolved}, status=status.HTTP_200_OK)


class UserTeamRequestView(ms.SwaggerViewMixin, ListAPIView):
    """
        View membership requests and team invitations for each user
    """
    swagger_title = 'membership requests'
    swagger_tags = ['Team']
    serializer_class = serializers.UserTeamRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        invitations = models.TeamInvitation.objects.filter(invitee=user)
        join_requests = models.TeamJoinRequest.objects.filter(user=user)
        return list(invitations) + list(join_requests)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class RemoveTeamMemberView(ms.SwaggerViewMixin, mixins.DeleteViewMixin, APIView):
    """
        View to remove a team member
    """
    swagger_title = 'membership requests'
    swagger_tags = ['Team']
    permission_classes = (per.IsAdminOrProjectAdmin,)
    serializer_class = serializers.RemoveTeamMemberSerializer
    serializer_response = serializers.RemoveTeamMemberResponseSerializers

    def delete(self, request, *args, **kwargs):
        return self.delete_instance(request)

    def get_instance(self):

        user_id = self.validated_data['user_id']
        team_id = self.validated_data['team_id']
        team_membership = models.TeamMembership.objects.get(user_id=user_id, team_id=team_id)

        if not team_membership:
            raise exceptions.NotFoundTeam()

        is_team_member(self.request.user, team_membership.team)
        removed_user = team_membership.user
        team_name = team_membership.team.name

        notification = create_notify(
            to_user=removed_user,
            title=_("Team Removal"),
            description=_("You have been removed from team '{team}'").format(
                team=team_name,
                admin=self.request.user.full_name()
            ),
            kwargs={
                'team_name': team_name,
                'type': 'TEAM_REMOVE'
            }
        )

        if notification.type == NotificationType.EMAIL:
            dispatch_email_notification(notification)

        return team_membership






