from django.contrib.auth.models import AbstractUser
from django.db import models


class Position(models.Model):
    """Employee positions (Developer, QA, Designer, etc.)"""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class TaskType(models.Model):
    """Types of tasks (Bug, New Feature, Refactoring)"""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    """Users (employees) with positions"""

    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workers",
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.position})"


class Task(models.Model):
    """Tasks for the team"""

    class PriorityChoices(models.TextChoices):
        URGENT = "URGENT", "Urgent"
        HIGH = "HIGH", "High"
        MEDIUM = "MEDIUM", "Medium"
        LOW = "LOW", "Low"

    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM
    )
    task_type = models.ForeignKey(
        TaskType, on_delete=models.SET_NULL, null=True, blank=True
    )
    assignees = models.ManyToManyField(
        Worker,
        related_name="tasks",
        blank=True,
        through="TaskWorker",
    )
    created_by = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="created_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TaskWorker(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
