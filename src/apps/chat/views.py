from django.db.models import Q, Count

from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.core.swagger import mixins as ms

from . import models, serializers


class ChatRoomCreateView(ms.SwaggerViewMixin, CreateAPIView):
    """
        chat room create
    """
    swagger_title = 'Chat creation'
    swagger_tags = ['Chat']
    serializer_class = serializers.ChatRoomCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        serializer.save()


class UnreadRoomListView(ms.SwaggerViewMixin, APIView):
    """
        unread chats view
    """
    swagger_title = 'Chat unread list'
    swagger_tags = ['Chat']
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        rooms_with_unread = models.ChatRoomModel.objects \
            .filter(participants=user) \
            .annotate(unread_count=Count(
                'messages',
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
            )) \
            .filter(unread_count__gt=0)

        serializer = serializers.ChatRoomCreateSerializer(rooms_with_unread, many=True)
        return Response(serializer.data)


class ChatRoomSummaryListView(ListAPIView):
    """
        summery chat view
    """
    swagger_title = 'Chat summery list'
    swagger_tags = ['Chat']
    serializer_class = serializers.ChatRoomSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.ChatRoomModel.objects.filter(participants=self.request.user)

