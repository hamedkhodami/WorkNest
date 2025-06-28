from rest_framework import serializers
from .models import Notification
from .enums import NotificationType, NotificationStatus


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for user notifications
    """
    type = serializers.ChoiceField(choices=NotificationType.choices, read_only=True)
    status = serializers.ChoiceField(choices=NotificationStatus.choices, read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'status',
            'title',
            'description',
            'is_visited',
            'retry_count',
            'sent_at',
            'created_at',
        ]
        read_only_fields = ('is_visited', 'retry_count', 'sent_at', 'created_at')


class NotificationResponseSerializer(serializers.Serializer):
    data = NotificationSerializer(many=True)