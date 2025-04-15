from django.urls import path, include
from accounts.views import SignUpView

from accounts.views import *

app_name = "accounts"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("", include("django.contrib.auth.urls")),
]