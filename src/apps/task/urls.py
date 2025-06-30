from django.urls import path

from . import views

app_name = 'apps.task'


urlpatterns = [
    path('tasklist/create/', views.TaskListCreationView.as_view(), name='task-create'),
    path('tasklist/delete/', views.TaskListDeleteView.as_view(), name='task-delete'),
    path('tasklist/task-lists/', views.AllTaskListsView.as_view(), name='task-list'),
    path('tasklist/<uuid:tasklist_id>/detail/', views.TaskListsDetailView.as_view(), name='tasklist-detail'),

    path('assign/', views.AddTaskToUserView.as_view(), name='assign-task-to-user'),
    path('remove-task/', views.RemoveTaskView.as_view(), name='remove-task'),
    path('<uuid:task_id>/update/', views.TaskUpdateView.as_view(), name='task-update'),
    path('<uuid:task_id>/detail/', views.TaskDetailView.as_view(), name='task-detail'),

]
