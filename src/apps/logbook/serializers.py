from rest_framework import serializers

from . import models


class LogEntrySerializer(serializers.ModelSerializer):
    """
        Serializers to list log
    """
    event_display = serializers.CharField(source='get_event_display', read_only=True)

    class Meta:
        model = models.LogEntryModel
        fields = [
            'id',
            'event',
            'event_display',
            'actor',
            'team',
            'board',
            'target_id',
            'target_repr',
            'extra_data',
            'created_at',
        ]
        read_only_fields = fields


class LogEntryListResponseSerializer(serializers.Serializer):
    data = LogEntrySerializer(many=True)


class ActivityPerDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    count = serializers.IntegerField()


class TopActorSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    email = serializers.EmailField()
    activity_count = serializers.IntegerField()


class PopularBoardSerializer(serializers.Serializer):
    board_id = serializers.UUIDField()
    board_title = serializers.CharField()
    team_id = serializers.UUIDField()
    activity_count = serializers.IntegerField()


class LogbookStatsDashboardSerializer(serializers.Serializer):
    activity_trend = ActivityPerDaySerializer(many=True)
    top_actors = TopActorSerializer(many=True)
    popular_boards = PopularBoardSerializer(many=True)