from django.urls import path
from . import views

app_name = 'apps.logbook'


urlpatterns = [
    path('', views.LogEntryListView.as_view(), name="log-list"),
    path("dashboard/", views.LogbookStatsDashboardView.as_view(), name="logbook-dashboard"),
]
