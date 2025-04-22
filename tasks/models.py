from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel


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


class Task(TimeStampedModel, models.Model):
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
        through="TaskAssignment",
        through_fields=("task", "worker"),
    )
    related_tasks = models.ManyToManyField(
        "self",
        through="TaskRelationship",
        through_fields=("source_task", "target_task"),
        symmetrical=False,
        blank=True,
        verbose_name="Related Tasks",
    )
    created_by = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="created_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["task", "worker"]]


class UserActivity(models.Model):
    ACTIVITY_CHOICES = [
        ("PROFILE_UPDATE", "Profile Updated"),
        ("TASK_COMPLETE", "Task Completed"),
        ("TASK_REOPENED", "Task Reopened"),
        ("TASK_ASSIGNED", "Task Assigned"),
    ]

    user = models.ForeignKey(Worker, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "User Activities"

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} at {self.timestamp}"


class Document(models.Model):
    file = models.FileField(upload_to="task_documents/")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(Worker, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.task.title}"


class TaskRelationship(models.Model):
    class RelationshipType(models.TextChoices):
        BLOCKS = "BLOCKS", "Blocks"
        DEPENDS_ON = "DEPENDS_ON", "Depends On"
        RELATED = "RELATED", "Related"
        DUPLICATE = "DUPLICATE", "Duplicate"
        PART_OF = "PART_OF", "Part Of"

    source_task = models.ForeignKey(
        "Task", on_delete=models.CASCADE, related_name="outgoing_relationships"
    )
    target_task = models.ForeignKey(
        "Task", on_delete=models.CASCADE, related_name="incoming_relationships"
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=RelationshipType.choices,
        default=RelationshipType.RELATED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Worker, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = [("source_task", "target_task")]
        verbose_name = "Task Relationship"
        verbose_name_plural = "Task Relationships"

    def __str__(self):
        return f"{self.source_task} → {self.target_task} ({self.get_relationship_type_display()})"
