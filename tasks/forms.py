from django import forms
from django.contrib.auth.forms import UserCreationForm

from tasks.models import (
    Position,
    Task,
    Worker,
)


class WorkerCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    position = forms.ModelChoiceField(queryset=Position.objects.all(), required=True)

    class Meta:
        model = Worker
        fields = ("username", "email", "position", "password1", "password2")


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "deadline",
            "priority",
            "task_type",
            "assignees",
        ]
        widgets = {
            "assignees": forms.CheckboxSelectMultiple,
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
