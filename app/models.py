import requests
from http.client import responses
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

    def update_status(self, bg_only=True):
        self.http_status = self.get_http_status()
        if self.use_health_check or not bg_only:
            self.health_check = self.get_health_check_data()
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
        verbose_name=_('Use Django Prometheus metrics'), default=False
    )
    bg_update = models.BooleanField(
        verbose_name=_('Update in background'), default=False
    )
    last_update = models.DateTimeField(auto_now=True, verbose_name=_('Last update'))

    http_status = models.PositiveIntegerField(
        verbose_name=_('HTTP Status'), null=True, blank=True
    )
    health_check = models.JSONField(
        verbose_name=_('Health Check Status'), null=True, blank=True
    )
