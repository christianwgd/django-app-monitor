from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from app.models import Application

class Command(BaseCommand):
    help = _('Update status of apps with background update True')

    def handle(self, *args, **options):

        apps = Application.objects.filter(bg_update=True)
        for app in apps:
            app.update_status()

