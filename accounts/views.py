from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import WorkerCreationForm


class SignUpView(CreateView):
    form_class = WorkerCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("tasks:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("tasks:profile")
