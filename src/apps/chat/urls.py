from django.urls import path

from . import views

app_name = 'apps.chat'


urlpatterns = [
    path('rooms/', views.ChatRoomCreateView.as_view(), name='chatroom-create'),
    path('rooms/unread/', views.UnreadRoomListView.as_view(), name='chatroom-unread'),
    path('rooms/summary/', views.ChatRoomSummaryListView.as_view(), name='chatroom-summary'),
]
