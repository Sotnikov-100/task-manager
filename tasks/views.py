from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from tasks.forms import TaskForm, DocumentForm, TaskRelationshipForm
from tasks.models import Task, Worker, UserActivity, Document, TaskRelationship


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        assigned_tasks = Task.objects.filter(assignees=user).order_by("-deadline")[:5]

        total_tasks = Task.objects.filter(assignees=user).count()
        completed_tasks = Task.objects.filter(assignees=user, is_completed=True).count()

        overdue_tasks = Task.objects.filter(
            assignees=user, deadline__lt=timezone.now(), is_completed=False
        ).count()

        context.update(
            {
                "assigned_tasks": assigned_tasks,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
            }
        )

        return context


class ProfileView(LoginRequiredMixin, DetailView):
    model = Worker
    template_name = "profile.html"
    context_object_name = "worker"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        tasks = Task.objects.filter(assignees=user)
        context["tasks"] = tasks
        context["tasks_completed"] = tasks.filter(is_completed=True).count()
        context["tasks_pending"] = tasks.filter(is_completed=False).count()

        context["user_activities"] = UserActivity.objects.filter(user=user).order_by(
            "-timestamp"
        )[:10]

        return context


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    paginate_by = 5
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_priority_choices"] = Task.PriorityChoices.choices
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(assignees=self.request.user)

        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if status == "completed":
            queryset = queryset.filter(is_completed=True)
        elif status == "active":
            queryset = queryset.filter(is_completed=False)

        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset.order_by("-deadline")


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:task-list")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task-list")


class TaskToggleCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        if request.user in task.assignees.all() or request.user == task.created_by:
            task.is_completed = not task.is_completed
            task.save()
            return JsonResponse(
                {
                    "status": "success",
                    "is_completed": task.is_completed,
                    "task_id": task.id,
                    "new_status": "Completed" if task.is_completed else "In Progress",
                }
            )
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)


class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = "tasks/document_upload.html"

    def form_valid(self, form):
        form.instance.task = Task.objects.get(pk=self.kwargs["pk"])
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("tasks:task-detail", kwargs={"pk": self.kwargs["pk"]})


class TaskRelationshipCreateView(LoginRequiredMixin, CreateView):
    model = TaskRelationship
    form_class = TaskRelationshipForm
    template_name = "tasks/task_relationship_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["source_task"] = get_object_or_404(Task, pk=self.kwargs["pk"])
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.source_task = get_object_or_404(Task, pk=self.kwargs["pk"])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("tasks:task-detail", kwargs={"pk": self.kwargs["pk"]})


class TaskRelationshipDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskRelationship
    template_name = "tasks/task_relationship_confirm_delete.html"

    def get_success_url(self):
        return reverse("tasks:task-detail", kwargs={"pk": self.object.source_task.pk})
