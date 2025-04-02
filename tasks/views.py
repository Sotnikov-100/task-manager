from django.shortcuts import render
from django.utils import timezone
from tasks.models import Task


def index(request):
    if request.user.is_authenticated:
        assigned_tasks = Task.objects.filter(
            assignees=request.user
        ).order_by("-deadline")[:5]

        total_tasks = Task.objects.filter(assignees=request.user).count()
        completed_tasks = Task.objects.filter(
            assignees=request.user,
            is_completed=True
        ).count()

        overdue_tasks = Task.objects.filter(
            assignees=request.user,
            deadline__lt=timezone.now(),
            is_completed=False
        ).count()
    else:
        assigned_tasks = []
        total_tasks = 0
        completed_tasks = 0
        overdue_tasks = 0

    context = {
        "assigned_tasks": assigned_tasks,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
    }
    return render(request, "tasks/index.html", context)
