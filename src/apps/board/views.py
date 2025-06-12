from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions as base_permissions

from apps.core.views import mixins
from apps.core.swagger import mixins as ms
from apps.core import text
from apps.account.auth import permissions as per
from apps.account.models import User

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
        response_data = self.create(request, response=False, *args, **kwargs)
        return Response(response_data, status=status.HTTP_201_CREATED)


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
        return board


# TODO : TEST
class DeleteBoardView(ms.SwaggerViewMixin, mixins.DeleteViewMixin, APIView):
    """
     delete board view
    """

    swagger_title = 'Board delete'
    swagger_tags = ['Board']
    permission_classes = (per.IsAdminOrProjectAdmin,)

    serializer = serializers.DeleteBoardSerializers
    serializer_response = serializers.MessageSerializer

    def delete(self, request, *args, **kwargs):
        ser = self.serializer(data=self.request.data)
        ser.is_valid(raise_exception=True)
        board = self.get_instance()
        board.delete()

        response_data = {"message": text.success_delete}
        return Response(response_data, status=status.HTTP_200_OK)

    def get_instance(self):
        board_id = self.validated_data["board_id"]
        team_id = self.validated_data["team_id"]

        board = models.BoardModel.objects.filter(id=board_id, team_id=team_id).first()
        if not board:
            raise exceptions.NotFoundBoard()

        return board







