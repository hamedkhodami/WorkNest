from django.urls import path

from . import views

app_name = 'apps.task'


urlpatterns = [
    path('create/', views.TaskCreationView.as_view(), name='task-create'),
    path('delete/', views.TaskListDeleteView.as_view(), name='task-delete'),
    path('task-lists/', views.TaskListsView.as_view(), name='task-list'),
]
