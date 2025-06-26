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
