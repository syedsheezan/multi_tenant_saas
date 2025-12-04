from django.urls import path
from .views import TaskListCreateView, TaskDetailView

urlpatterns = [
    path('<uuid:project_id>/', TaskListCreateView.as_view(), name="task-list-create"),
    path('detail/<uuid:pk>/', TaskDetailView.as_view(), name="task-detail"),
]
