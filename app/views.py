from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from app.models import Application


class AppList(LoginRequiredMixin, ListView):
    model = Application

    def get_queryset(self):
        apps = Application.objects.filter(admins=self.request.user)
        for app in apps:
            app.code, app.text = app.get_http_status()
            if app.use_health_check:
                app.detail = app.get_health_check_data()
        return apps
