from django import forms
from django.utils import timezone

from tasks.models import Task


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

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
