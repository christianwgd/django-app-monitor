from urllib.parse import urljoin

import requests
from http.client import responses

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib import auth


User = auth.get_user_model()

REQUEST_TIMEOUT = getattr(settings, 'REQUEST_TIMEOUT', 20)
OK_VALUES = getattr(settings, 'HEALTH_CHECK_OK_VALUES', ['OK'])

FREQUENCY_CHOICES = (
    (5, '5'),
    (10, '10'),
    (15, '15'),
    (30, '30'),
)


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

    def get_absolute_url(self):
        return reverse('app:detail', kwargs={'pk': self.id})

    def get_absolute_uri(self):
        domain = getattr(settings, 'DEFAULT_DOMAIN', 'https://monitor.wgdnet.de')
        return urljoin(domain, self.get_absolute_url())

    def is_due(self, cron_minute):
        m5 = 5 * round(cron_minute / 5)
        return m5 % self.frequency == 0

    def get_http_status(self):
        try:
            r = requests.get(f'{self.url}/', timeout=self.timeout)
            rc = r.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            rc = 408
        if rc != 200:
            Alert.objects.create(
                app=self,
                typus=_('HTTP Status'),
                value=f'{rc} {responses[rc]}'
            )
        return rc

    @property
    def get_http_status_text(self):
        if self.http_status:
            return responses[self.http_status]
        return ''

    def get_health_check_data(self):
        headers = {'Accept': 'application/json'}
        try:
            r = requests.get(f'{self.url}/ht/', headers=headers, timeout=self.timeout)
            if r.status_code == 200:
                return r.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        return {}

    def create_process_metric(self):
        token = getattr(settings, 'PROCESS_METRICS_TOKEN', None)
        if token:
            try:
                headers = {'Accept': 'application/json', 'token': token}
                r = requests.get(f'{self.url}/metrics/', headers=headers, timeout=self.timeout)
                if r.status_code == 200:
                    json_metrics = r.json()
                    SystemMetric.objects.create(
                        app=self,
                        cpu_percent=json_metrics['cpu_percent'],
                        mem_percent=json_metrics['mem_percent'],
                    )
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass

    def update_status(self):
        self.http_status = self.get_http_status()
        if self.use_health_check:
            self.health_check = self.get_health_check_data()
        if self.use_metrics:
            self.create_process_metric()
        self.save()

    @property
    def metric_days_in_hours(self):
        return self.metric_days * 24

    def is_working(self):
        if self.http_status != 200:
            return False
        if self.use_health_check:
            for _key, value in self.health_check.items():
                if value not in OK_VALUES:
                    return False
        return True

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

    max_cpu_percent = models.FloatField(
        verbose_name=_('Max. CPU Percentage'), default=0.8
    )
    max_mem_percent = models.FloatField(
        verbose_name=_('Max. Memory Percentage'), default=0.8
    )
    alert_sent = models.BooleanField(
        verbose_name=_('Alert sent'), default=False
    )
    metric_days = models.PositiveIntegerField(
        verbose_name=_('Show metrics for number of days'), default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('After this time old metrics will be deleted')
    )
    frequency =  models.IntegerField(
        verbose_name=_('Test frequency'),
        choices=FREQUENCY_CHOICES, default=15,
    )
    timeout = models.PositiveSmallIntegerField(default=20, verbose_name=_('Timeout'))


class Alert(models.Model):
    """
    Log status info
    """

    class Meta:
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')
        ordering = ['-timestamp']

    timestamp = models.DateTimeField(auto_now=True, verbose_name=_('Timestamp'))
    app = models.ForeignKey(
        Application, verbose_name=_('Application'),
        related_name='alerts', on_delete=models.CASCADE,
    )
    typus = models.CharField(verbose_name=_('Type'), max_length=50)
    value = models.CharField(verbose_name=_('Value'), max_length=50)


class SystemMetric(models.Model):
    """
    Process metrics from psutil
    """

    class Meta:
        verbose_name = _('System metric')
        verbose_name_plural = _('System metrics')
        ordering = ['timestamp']

    timestamp = models.DateTimeField(auto_now=True, verbose_name=_('Timestamp'))
    app = models.ForeignKey(
        Application, verbose_name=_('Application'),
        related_name='metrics', on_delete=models.CASCADE,
    )
    cpu_percent = models.FloatField(verbose_name=_('CPU percent'), default=0.0)
    mem_percent = models.FloatField(verbose_name=_('Memnory percent'), default=0.0)
