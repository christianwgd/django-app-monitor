from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _

from app.models import Application


class AppList(LoginRequiredMixin, ListView):
    model = Application

    def get_queryset(self):
        return Application.objects.filter(admins=self.request.user)


@require_http_methods(["GET"])
def instant_update(request, app_id):
    try:
        app = Application.objects.get(pk=app_id)
        app.update_status()
        messages.success(request, _('App status updated for {name}').format(name=app.name))
    except Application.DoesNotExist:
        pass
    return redirect(reverse('app:list'))


@require_http_methods(["GET"])
def instant_update_all(request):
    for app in Application.objects.all():
        app.update_status()
    messages.success(request, _('App status updated for all applications'))
    return redirect(reverse('app:list'))
