from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from app.models import Application


class Command(BaseCommand):
    help = _('Update status of apps with background update True')

    def handle(self, *args, **options):

        apps = Application.objects.filter(bg_update=True)
        for app in apps:
            app.update_status()
            if not app.is_working():
                if not app.alert_sent:
                    subject = _('Monitoring Alert: {name}').format(name=app.name)
                    message = _(
                        'Please check service {name} {url}'
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
            else:
                app.alert_sent = False
            app.save()


