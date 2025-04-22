from django import forms
from django.db.models import Q
from django.utils import timezone

from tasks.models import Task, Document, TaskRelationship


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


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file"]


class TaskRelationshipForm(forms.ModelForm):
    class Meta:
        model = TaskRelationship
        fields = ["target_task", "relationship_type"]
        widgets = {
            "target_task": forms.Select(attrs={"class": "form-select"}),
            "relationship_type": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.source_task = kwargs.pop("source_task", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and self.source_task:
            self.fields["target_task"].queryset = (
                Task.objects.filter(Q(assignees=self.user) | Q(created_by=self.user))
                .exclude(pk=self.source_task.pk)
                .distinct()
            )
