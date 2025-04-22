from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from tasks.models import UserActivity, Task, Worker


@receiver(post_save, sender=Worker)
def create_profile_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(
            user=instance,
            activity_type="PROFILE_UPDATE",
            description="Profile created",
            metadata={"action": "registration"},
        )


@receiver(m2m_changed, sender=Task.assignees.through)
def create_task_assignment_activity(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for worker_id in pk_set:
            worker = Worker.objects.get(pk=worker_id)
            UserActivity.objects.create(
                user=worker,
                activity_type="TASK_ASSIGNED",
                description=f'You were assigned to task "{instance.title}"',
                metadata={"task_id": instance.id, "task_title": instance.title},
            )


@receiver(post_save, sender=Task)
def update_task_completion_activity(sender, instance, created, **kwargs):
    if not created and hasattr(instance, "_changed_fields"):
        if "is_completed" in instance._changed_fields:
            for worker in instance.assignees.all():
                UserActivity.objects.create(
                    user=worker,
                    activity_type=(
                        "TASK_COMPLETE" if instance.is_completed else "TASK_REOPENED"
                    ),
                    description=f'Task "{instance.title}" was marked as '
                    f'{"completed" if instance.is_completed else "reopened"}',
                    metadata={
                        "task_id": instance.id,
                        "task_title": instance.title,
                        "status": "completed" if instance.is_completed else "reopened",
                    },
                )
