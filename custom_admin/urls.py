# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_dashboard, name='task_dashboard'),
    path('start-task/<str:task_name>/', views.start_task, name='start_task'),
    path('get-task-progress/<str:task_name>/', views.get_task_progress, name='get_task_progress'),
]
