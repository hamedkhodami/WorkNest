from django.urls import path

from . import views

app_name = 'apps.notification'


urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
]
