from django.contrib import admin
from tasks.models import Position, Task, TaskType, Worker, TaskAssignment


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "position")
    list_filter = ("position",)
    search_fields = ("username", "email")


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ("task", "worker", "assigned_at")
    list_filter = ("assigned_at",)
    raw_id_fields = ("task", "worker")


class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 1
    raw_id_fields = ("worker",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "task_type", "deadline", "created_at")
    list_filter = ("priority", "task_type", "is_completed")
    search_fields = ("title", "description")
    inlines = (TaskAssignmentInline,)
    readonly_fields = ("created_at",)


admin.site.register(Position)
admin.site.register(TaskType)
