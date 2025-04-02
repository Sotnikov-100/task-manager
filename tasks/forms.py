from django import forms
from django.contrib.auth.forms import UserCreationForm

from tasks.models import Position, Worker


class WorkerCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=True
    )

    class Meta:
        model = Worker
        fields = ("username", "email", "position", "password1", "password2")
