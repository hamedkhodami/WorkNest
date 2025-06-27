from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.core import text
from . import models

User = get_user_model()


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )

    class Meta:
        model = models.ChatRoomModel
        fields = ['id', 'participants', 'created_at']

    def validate_participants(self, value):
        if len(value) != 2:
            raise serializers.ValidationError(text.two_user_in_room)
        return value

    def create(self, validated_data):
        users = validated_data.pop('participants')
        user1, user2 = users[0], users[1]

        existing_room = models.ChatRoomModel.objects \
            .filter(participants=user1) \
            .filter(participants=user2) \
            .distinct().first()

        if existing_room:
            return existing_room

        room = models.ChatRoomModel.objects.create(**validated_data)
        room.participants.set(users)
        return room


class ChatRoomSummarySerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    opponent = serializers.SerializerMethodField()

    class Meta:
        model = models.ChatRoomModel
        fields = ['id', 'opponent', 'last_message', 'unread_count', 'created_at']

    def get_opponent(self, obj):
        request_user = self.context['request'].user
        opponent = obj.participants.exclude(id=request_user.id).first()
        if opponent:
            return {
                'id': str(opponent.id),
                'full_name': opponent.full_name(),
                'phone_number': opponent.raw_phone_number,
            }
        return None

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {
                'content': msg.content,
                'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()