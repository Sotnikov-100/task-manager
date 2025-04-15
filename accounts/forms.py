from django.contrib.auth.forms import UserCreationForm
from tasks.models import Worker, Position
from django import forms


class WorkerCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    position = forms.ModelChoiceField(queryset=Position.objects.all(), required=True)

    class Meta:
        model = Worker
        fields = ("username", "email", "position", "password1", "password2")
