from django.urls import path

from . import views

app_name = 'apps.task'


urlpatterns = [
    path('create/', views.TaskListCreationView.as_view(), name='task-create'),
    path('delete/', views.TaskListDeleteView.as_view(), name='task-delete'),
    path('task-lists/', views.TaskListsView.as_view(), name='task-list'),
    path('<uuid:tasklist_id>/', views.TaskListsDetailView.as_view(), name='tasklist-detail'),

    path('task/assign/', views.AddTaskToUserView.as_view(), name='assign-task-to-user'),
    path('task/remove-task/', views.RemoveTaskView.as_view(), name='remove-task'),
    path('task/<uuid:task_id>/update/', views.TaskUpdateView.as_view(), name='task-update'),
    path('task/<uuid:task_id>/detail/', views.TaskDetailView.as_view(), name='task-detail'),

]
