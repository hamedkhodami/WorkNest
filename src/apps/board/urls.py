from django.urls import path

from . import views

app_name = 'apps.board'


urlpatterns = [
    path('create/', views.CreateBoardView.as_view(), name='board-create'),
    path('list-boards/', views.BoardsTeamsView.as_view(), name='boards_teams'),
    path('<uuid:board_uuid>/', views.DetailBoardView.as_view(), name='board-detail'),
    path("delete/", views.DeleteBoardView.as_view(), name="board-delete"),
]





