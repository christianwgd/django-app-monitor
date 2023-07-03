import requests
from http.client import responses

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib import auth


User = auth.get_user_model()


class Application(models.Model):
    """
    An app that should be monitored
    """

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_http_status(self):
        r = requests.get(f'{self.url}/', timeout=20)
        return r.status_code

    @property
    def get_http_status_text(self):
        if self.http_status:
            return responses[self.http_status]
        return ''

    def get_health_check_data(self):
        headers = {'Accept': 'application/json'}
        r = requests.get(f'{self.url}/ht/', headers=headers, timeout=20)
        if r.status_code == 200:
            return r.json()
        return {}

    def create_process_metric(self):
        token = getattr(settings, 'PROCESS_METRICS_TOKEN', None)
        if token:
            headers = {'Accept': 'application/json', 'token': token}
            r = requests.get(f'{self.url}/process/metrics/', headers=headers, timeout=20)
            if r.status_code == 200:
                json_metrics = r.json()
                ProcessMetric.objects.create(
                    app=self,
                    cpu_time=sum(json_metrics['cpu_times']),
                    cpu_percent=json_metrics['cpu_percent'],
                    mem_vrt=json_metrics['memory_info'][1],
                    mem_rss=json_metrics['memory_info'][0],
                    mem_percent=json_metrics['memory_percent'],
                )

    def update_status(self, bg_only=True):
        self.http_status = self.get_http_status()
        if self.use_health_check or not bg_only:
            self.health_check = self.get_health_check_data()
        if self.use_metrics:
            self.create_process_metric()
        self.save()

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    url = models.URLField(verbose_name=_('URL'))
    admins = models.ManyToManyField(
        User, verbose_name=_('Administrators'), related_name='apps'
    )
    logo = models.ImageField(
        max_length=255, upload_to='apps/', verbose_name=_('Logo'),
        null=True, blank=True
    )
    notify_by_email = models.BooleanField(
        verbose_name=_('Notify by email'), default=False,
    )
    use_health_check = models.BooleanField(
        verbose_name=_('Use Django health check'), default=False
    )
    use_metrics = models.BooleanField(
        verbose_name=_('Use psutil metrics'), default=False
    )
    bg_update = models.BooleanField(
        verbose_name=_('Update in background'), default=False
    )
    last_update = models.DateTimeField(
        auto_now=True, verbose_name=_('Last update'),
        null=True, blank=True

    )

    http_status = models.PositiveIntegerField(
        verbose_name=_('HTTP Status'), null=True, blank=True
    )
    health_check = models.JSONField(
        verbose_name=_('Health Check Status'), null=True, blank=True
    )


class ProcessMetric(models.Model):
    """
    Process metrics from psutil
    """

    class Meta:
        verbose_name = _('Process metric')
        verbose_name_plural = _('Process metrics')
        ordering = ['timestamp']

    timestamp = models.DateTimeField(auto_now=True, verbose_name=_('Timestamp'))
    app = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name=_('Application'))
    cpu_time = models.FloatField(verbose_name=_('CPU time'), default=0.0)
    cpu_percent = models.FloatField(verbose_name=_('CPU percent'), default=0.0)
    mem_rss = models.FloatField(verbose_name=_('Memory (resident)'), default=0.0)
    mem_vrt = models.FloatField(verbose_name=_('Memory (virtual)'), default=0.0)
    mem_percent = models.FloatField(verbose_name=_('Memnory percent'), default=0.0)
