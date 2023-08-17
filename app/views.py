from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import formats
from django.utils.timezone import now, localtime
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _
from chartjs.views.lines import BaseLineChartView

from app.models import Application, SystemMetric


class AppList(LoginRequiredMixin, ListView):
    model = Application

    def get_queryset(self):
        return Application.objects.filter(admins=self.request.user)


class AppDetail(UserPassesTestMixin, DetailView):
    model = Application

    def test_func(self):
        return self.request.user in self.get_object().admins.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['value_names'] = [
            ('cpu_percent', '%'), ('mem_percent', '%')
        ]
        context['hours'] = self.object.metric_days * 24
        return context


@require_http_methods(["GET"])
def instant_update(request, app_id):
    if 'HTTP_REFERER' in request.META:
        referer = request.META['HTTP_REFERER']
    else:
        referer = reverse('app:list')
    try:
        app = Application.objects.get(pk=app_id)
        app.update_status()
        messages.success(request, _('App status updated for {name}').format(name=app.name))
    except Application.DoesNotExist:
        pass
    return redirect(referer)


@require_http_methods(["GET"])
def instant_update_all(request):
    for app in Application.objects.all():
        app.update_status()
    messages.success(request, _('App status updated for all applications'))
    return redirect(reverse('app:list'))


class ValuesJSONView(BaseLineChartView):
    value_name = None
    queryset = None

    def get(self, request, *args, **kwargs):
        self.value_name = kwargs.get('name')
        app = Application.objects.get(id=kwargs.get('app_id'))
        from_time = now() - timedelta(hours=24 * app.metric_days)
        self.queryset = SystemMetric.objects.filter(
            app=app, timestamp__gte=from_time
        ).order_by('timestamp')
        return super().get(request, *args, **kwargs)

    def get_providers(self):
        return [self.value_name]

    def get_labels(self):
        return [formats.date_format(localtime(item.timestamp), 'H:i') for item in self.queryset]

    def get_data(self):
        return [[round(getattr(item, self.value_name), 2) for item in self.queryset]]

    def get_colors(self):
        return iter([(120, 120, 120)])
