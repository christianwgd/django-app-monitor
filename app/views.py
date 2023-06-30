from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from app.models import Application


class AppList(LoginRequiredMixin, ListView):
    model = Application

    def get_queryset(self):
        apps = Application.objects.filter(admins=self.request.user)
        for app in apps:
            status = app.get_status()
            app.code = status['code']
            app.text = status['text']
            if app.code == 200:
                app.detail = status['detail']
        return apps
