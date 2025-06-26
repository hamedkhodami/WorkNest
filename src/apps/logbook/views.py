from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.core.views import mixins
from apps.core.swagger import mixins as ms
from apps.account.auth import permissions as per
from apps.core import text
from apps.core.services.access_control import is_team_member

from . import models, serializers


class LogEntryListView(ms.SwaggerViewMixin, mixins.ListViewMixin, APIView):
    """
        View to list log
    """
    swagger_title = "List Log"
    swagger_tags = ["LogBook"]
    permission_classes = (per.IsTeamUser,)
    serializer = serializers.LogEntrySerializer
    page_size = 20

    def get_queryset(self):

        self.query_params = self.get_data_params()
        queryset = models.LogEntryModel.objects.all()

        team_id = self.query_params.get("team")
        board_id = self.query_params.get("board")

        if team_id:
            queryset = queryset.filter(team_id=team_id)
            is_team_member(self.request.user, team_id)

        if board_id:
            queryset = queryset.filter(board_id=board_id)

        return queryset

    def get(self, request, *args, **kwargs):
        response_data = self.list(request)

        if isinstance(response_data, Response):
            return response_data

        return Response({"data": response_data}, status=status.HTTP_200_OK)


