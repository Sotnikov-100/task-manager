from django.urls import path

from tasks.views import (
    IndexView,
    ProfileView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    TaskToggleCompleteView,
    DocumentUploadView,
)

app_name = "tasks"


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path(
        "tasks/<int:pk>/toggle-complete/",
        TaskToggleCompleteView.as_view(),
        name="task-toggle-complete",
    ),
    path(
        "tasks/<int:pk>/upload-document/",
        DocumentUploadView.as_view(),
        name="document-upload",
    ),
]
