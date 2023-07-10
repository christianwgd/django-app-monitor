from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from app.models import SystemMetric


class Command(BaseCommand):
    help = _('Delete metrics older than 24 hours')

    def handle(self, *args, **options):
        time = now() - timedelta(hours=24)
        delete_metrics = SystemMetric.objects.filter(
            timestamp__lt=time
        )
        delete_metrics.delete()


