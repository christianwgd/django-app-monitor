from logging import getLogger

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from app.models import Application

logger = getLogger('status_update')


class Command(BaseCommand):
    help = _('Update status of apps with background update True')

    def handle(self, *args, **options):

        apps = Application.objects.filter(bg_update=True)
        for app in apps:
            # Check according to selected frequency
            if app.is_due(now().minute):
                log_msg = f'{app.name} due'
                app.update_status()
                if not app.is_working():
                    log_msg += ', not ok'
                    if not app.alert_sent and app.notify_by_email:
                        subject = _('Monitoring Alert: {name}').format(name=app.name)
                        message = _(
                            'Please check service {name} at {url}.'
                        ).format(name=app.name, url=app.url)
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'wgdsrv@wgdnet.de')
                        recipient_list = [mgr.email for mgr in app.admins.all()]
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=from_email,
                            recipient_list=recipient_list,
                            fail_silently=False
                        )
                        app.alert_sent = True
                        log_msg += ', alert sent'
                else:
                    log_msg += ', ok'
                    app.alert_sent = False
                app.save()
            else:
                log_msg = f'{app.name} not due'
            logger.info(log_msg)


