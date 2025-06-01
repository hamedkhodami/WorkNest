from django.urls import path

from . import views

app_name = 'apps.team'


urlpatterns = [
    path('create/', views.TeamCreateView.as_view(), name='team_create'),
    path('my-teams/', views.UsersTeamsView.as_view(), name='user_teams')
]
