from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from tasks.models import Task, Worker

from .forms import WorkerCreationForm


@login_required
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


class SignUpView(generic.CreateView):
    form_class = WorkerCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("tasks:login")


class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    template_name = "profile.html"
    context_object_name = "worker"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(assignees=self.request.user)
        return context
