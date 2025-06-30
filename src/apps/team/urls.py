from django.urls import path

from . import views

app_name = 'apps.team'


urlpatterns = [
    path('create/', views.TeamCreateView.as_view(), name='team_create'),
    path('my-teams/', views.UsersTeamsView.as_view(), name='user_teams'),
    path('<uuid:team_id>/detail/', views.TeamDetailView.as_view(), name='team-detail'),
    path('<uuid:team_id>/update/', views.TeamUpdateViews.as_view(), name='team-update'),
    path('join/', views.JoinTeamView.as_view(), name='team-join'),
    path('join-request/<int:pk>/resolve/', views.ResultJoinTeamView.as_view(), name='resolve-join-request'),
    path('invite/', views.TeamInvitationRequestView.as_view(), name='team-invite'),
    path('invitations/<uuid:pk>/resolve/', views.ResultInvitationTeamView.as_view(), name='team-resolve-invite'),
    path('requests/', views.UserTeamRequestView.as_view(), name='user-team-requests'),
    path('remove-member/', views.RemoveTeamMemberView.as_view(), name='remove_team_member'),
]





