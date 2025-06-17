from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.views import mixins
from apps.core.swagger import mixins as ms
from apps.core.services.access_control import is_team_member
from apps.core import text
from apps.account.auth import permissions as per
from apps.team.models import TeamModel

from . import models, exceptions, serializers


class CreateBoardView(ms.SwaggerViewMixin, mixins.CreateViewMixin, APIView):
    """
      create new board view
    """
    swagger_title = 'Board creation'
    swagger_tags = ['Board']
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer = serializers.CreateBoardSerializer
    serializer_response = serializers.CreateBoardSerializerResponse

    def post(self, request, *args, **kwargs):
        team_id = request.data.get("team_id")
        team = TeamModel.objects.filter(id=team_id).first()

        is_team_member(request.user, team)

        response_data = self.create(request, response=False, *args, **kwargs)
        return Response(response_data, status=status.HTTP_201_CREATED)

    # TODO: Implement notification system


class BoardsTeamsView(ms.SwaggerViewMixin, APIView):
    """
     list of team boards serializers
    """

    swagger_title = 'boards Team'
    swagger_tags = ['board']
    serializer_class = serializers.BoardListSerializer
    permission_classes = (per.IsTeamUser,)

    def get(self, request):
        user_team = getattr(request.user, "team", None)

        is_archived = request.GET.get("is_archived", "").lower()
        is_archived = is_archived == "true" if is_archived in ["true", "false"] else None

        boards = models.BoardModel.objects.filter(team=user_team)
        if is_archived is not None:
            boards = boards.filter(is_archived=is_archived)

        serializer = self.serializer_class(boards, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailBoardView(ms.SwaggerViewMixin, mixins.DetailViewMixin, APIView):
    """
      views detail board
    """

    swagger_title = "Board Details"
    swagger_tags = ["Board"]
    serializer_response = serializers.DetailBoardSerializers
    permission_classes = (per.IsTeamUser,)

    def get(self, request, *args, **kwargs):
        return self.detail(request)

    def get_instance(self):
        board_uuid = self.kwargs.get('board_uuid')
        board = models.BoardModel.objects.filter(id=board_uuid).first()
        if not board:
            raise exceptions.NotFoundTeam()
        is_team_member(self.request.user, board.team)
        return board


class DeleteBoardView(ms.SwaggerViewMixin, mixins.DeleteViewMixin, APIView):
    """
        delete board view
    """

    swagger_title = "Board Delete"
    swagger_tags = ["Board"]
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer_response = serializers.BoardDeleteSerializer

    def delete(self, request, *args, **kwargs):
        return self.delete_instance(request)

    def get_instance(self):
        serializer = self.serializer_response(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        board = self.validated_data["board"]
        is_team_member(self.request.user, board.team)

        return board


class BoardUpdateViews(ms.SwaggerViewMixin, mixins.UpdateViewMixin, APIView):
    """
        board update view
    """
    swagger_title = 'Board Update'
    swagger_tags = ['Board']
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer = serializers.BoardUpdateSerializers
    serializer_response = serializers.BoardUpdateSerializersResponse

    def get_instance(self):
        board_id = self.kwargs.get('board_id')
        board = models.BoardModel.objects.filter(id=board_id).first()
        if not board:
            raise exceptions.NotFoundBoard()
        is_team_member(self.request.user, board.team)
        return board

    def put(self, request, *args, **kwargs):
        instance = self.get_instance()
        ser = self.serializer(instance, data=request.data, partial=True, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()

        return Response({
            'message': text.success_update,
            'update_data': ser.data
        }, status=200)









