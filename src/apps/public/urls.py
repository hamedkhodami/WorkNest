from django.urls import path

from . import views

app_name = 'apps.public'


urlpatterns = [
    path('user_viewer/', views.ViewerUserView.as_view(), name='user-viewer-list'),
    path('public_teams/', views.PublicTeamView.as_view(), name='public-team-list'),
]
