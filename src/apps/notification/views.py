from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.core.views import mixins
from apps.core.swagger import mixins as ms

from . import serializers, models


class NotificationListView(ms.SwaggerViewMixin, mixins.ListViewMixin, APIView):
    """
    View for user notifications
    """
    swagger_title = 'Notification List'
    swagger_tags = ['Notification']
    permission_classes = [permissions.IsAuthenticated]

    serializer = serializers.NotificationSerializer
    serializer_response = serializers.NotificationResponseSerializer

    def get_queryset(self):
        return models.Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        response_data = self.list(request)

        if isinstance(response_data, Response):
            return response_data

        return Response({"data": response_data}, status=status.HTTP_200_OK)
