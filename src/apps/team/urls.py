from django.urls import path

from . import views

app_name = 'apps.team'


urlpatterns = [
    path('create/', views.TeamCreateView.as_view(), name='team_create'),
    path('my-teams/', views.UsersTeamsView.as_view(), name='user_teams'),
    path('<uuid:team_id>/', views.TeamDetailView.as_view(), name='team-detail'),
    path('<uuid:team_id>/update/', views.TeamUpdateViews.as_view(), name='team-update'),
    path('join/', views.JoinTeamView.as_view(), name='team-join'),
    path('teams/join-request/<int:pk>/resolve/', views.ResultJoinTeamView.as_view(), name='resolve-join-request'),
]
