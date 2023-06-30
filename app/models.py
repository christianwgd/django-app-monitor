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

    def get_status(self):
        headers = {'Accept': 'application/json'}
        r = requests.get(f'{self.url}/ht/', headers=headers, timeout=20)
        status = {'code': r.status_code, 'text': responses[r.status_code]}
        if r.status_code == 200:
            status['detail'] = r.json()
        return status

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
