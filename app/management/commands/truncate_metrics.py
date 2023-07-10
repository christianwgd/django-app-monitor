from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from app.models import SystemMetric, Application


class Command(BaseCommand):
    help = _('Delete stale metrics')

    def handle(self, *args, **options):
        for app in Application.objects.all():
            time = now() - timedelta(hours=24 * app.metric_days)
            delete_metrics = SystemMetric.objects.filter(
                app=app, timestamp__lt=time
            )
            delete_metrics.delete()


