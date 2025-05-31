from django.urls import path

from . import views

app_name = 'apps.team'


urlpatterns = [
    path('create/', views.TeamCreateView.as_view(), name='team_create'),
]
