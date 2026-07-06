from logging import getLogger

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from app.models import Application

logger = getLogger('status_update')


class Command(BaseCommand):
    help = _('Check certificate expiration date')

    def handle(self, *args, **options):

        apps = Application.objects.filter(check_cert=True)
        for app in apps:
            # Check certificate, typotically every 24 hours
            log_msg = f'Check certificate for {app.name}'
            app.get_cert_validation_status()
            logger.info(log_msg)

