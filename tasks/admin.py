from django.contrib import admin
from tasks.models import Position, TaskType, Worker, Task


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "position"
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "priority",
        "task_type",
        "deadline"
    )
    filter_horizontal = ("assignees",)


admin.site.register(Position)
admin.site.register(TaskType)
