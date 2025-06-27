from django.db.models import Count
from django.db.models.functions import TruncDate

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
    serializer_response = serializers.LogEntryListResponseSerializer
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

        return Response({
            "data": response_data.get("results", response_data)
        })


class LogbookStatsDashboardView(ms.SwaggerViewMixin, APIView):
    """
    Dashboard view for log analytics:
    - Activity per day
    - Top active users
    - Most updated boards
    """
    swagger_title = "Dashboard Logbook"
    swagger_tags = ["LogBook"]
    permission_classes = (per.IsTeamUser,)
    serializer_class = serializers.LogbookStatsDashboardSerializer

    def get(self, request):
        team_id = request.query_params.get("team")
        logs = models.LogEntryModel.objects.all()

        if team_id:
            logs = logs.filter(team_id=team_id)
            is_team_member(request.user, team_id)

        activity_trend = (
            logs.annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("-date")[:10]
        )

        top_actors = (
            logs.values("actor__id", "actor__email")
            .annotate(activity_count=Count("id"))
            .order_by("-activity_count")[:5]
        )

        popular_boards = (
            logs.values("board__id", "board__title", "team__id")
            .annotate(activity_count=Count("id"))
            .order_by("-activity_count")[:5]
        )

        data = {
            "activity_trend": [
                {"date": row["date"], "count": row["count"]}
                for row in activity_trend
            ],
            "top_actors": [
                {
                    "user_id": row["actor__id"],
                    "email": row["actor__email"],
                    "activity_count": row["activity_count"],
                }
                for row in top_actors
            ],
            "popular_boards": [
                {
                    "board_id": row["board__id"],
                    "board_title": row["board__title"],
                    "team_id": row["team__id"],
                    "activity_count": row["activity_count"],
                }
                for row in popular_boards
            ],
        }

        serializer = self.serializer_class(data)
        return Response(serializer.data)
