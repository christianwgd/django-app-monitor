from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from app.models import Application


class AppList(LoginRequiredMixin, ListView):
    model = Application
