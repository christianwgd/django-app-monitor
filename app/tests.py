from datetime import timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from faker import Faker

from app.models import Application, SystemMetric, Alert

User = auth.get_user_model()


class ApplicationTest(TestCase):

    def setUp(self):
        self.fake = Faker()
        Faker.seed(0)

        self.admin = User.objects.create(
            username=self.fake.user_name(),
            email=self.fake.email(),
        )
        self.app = Application.objects.create(
            name=self.fake.word(),
            url='https://example.com',
            metric_days=1,
            frequency=5,
        )
        self.app.admins.add(self.admin)

    def test_app_str(self):
        self.assertEqual(str(self.app), self.app.name)

    def test_app_get_absolute_url(self):
        self.assertEqual(
            self.app.get_absolute_url(),
            reverse('app:detail', kwargs={'pk': self.app.id})
        )

    def test_app_get_absolute_uri(self):
        domain = getattr(settings, 'DEFAULT_DOMAIN', 'https://monitor.wgdnete.de')
        self.assertEqual(
            self.app.get_absolute_uri(),
            urljoin(domain, self.app.get_absolute_url())
        )

    def test_is_due_5(self):
        for m in range(0, 60, 5):
            self.assertTrue(self.app.is_due(m))

    def test_is_due_10(self):
        self.app.frequency = 10
        self.app.save()
        self.app.refresh_from_db()
        for m in range(0, 60, 10):
            self.assertTrue(self.app.is_due(m))
        for m in [5, 15, 25, 55]:
            self.assertFalse(self.app.is_due(m))

    def test_is_due_15(self):
        self.app.frequency = 15
        self.app.save()
        self.app.refresh_from_db()
        for m in range(0, 60, 15):
            self.assertTrue(self.app.is_due(m))
        for m in [5, 10, 20, 25, 55]:
            self.assertFalse(self.app.is_due(m))

    def test_app_get_http_status_200(self):
        record_count = Alert.objects.count()
        self.assertEqual(self.app.get_http_status(), 200)
        self.assertEqual(Alert.objects.count(), record_count)

    def test_app_get_http_status_404(self):
        self.app.url = 'https://example.com/not_found/'
        self.app.save()
        self.app.refresh_from_db()
        record_count = Alert.objects.count()
        self.assertEqual(self.app.get_http_status(), 404)
        self.assertEqual(Alert.objects.count(), record_count + 1)
        status_record = Alert.objects.latest('timestamp')
        self.assertEqual(status_record.app, self.app)
        self.assertEqual(status_record.typus, _('HTTP Status'))
        self.assertEqual(status_record.value, '404 Not Found')

    def test_app_get_health_check_data(self):
        self.assertEqual(
            self.app.get_health_check_data(),
            {}
        )

    def test_is_working_true(self):
        self.app.http_status = 200
        self.app.health_check = {
            "DiskUsage": "working", "MemoryUsage": "working",
            "DatabaseBackend": "working", "MigrationsHealthCheck": "working"
        }
        self.app.use_health_check = True
        self.app.save()
        self.app.refresh_from_db()
        self.assertTrue(self.app.is_working())

    def test_is_working_false_http_status(self):
        self.app.http_status = 404
        self.app.save()
        self.app.refresh_from_db()
        self.assertFalse(self.app.is_working())

    def test_is_working_false_health_check(self):
        self.app.http_status = 200
        self.app.health_check = {
            "DiskUsage": "working", "MemoryUsage": "working",
            "DatabaseBackend": "error", "MigrationsHealthCheck": "working"
        }
        self.app.use_health_check = True
        self.app.save()
        self.app.refresh_from_db()
        self.assertFalse(self.app.is_working())

    def test_app_update_status(self):
        self.app.bg_update = True
        self.app.save()
        self.app.refresh_from_db()
        self.app.update_status()
        self.assertEqual(self.app.http_status, 200)
        self.assertEqual(self.app.last_update.date(), now().date())

    def test_app_metric_days_in_hours(self):
        self.assertEqual(self.app.metric_days_in_hours, self.app.metric_days * 24)

    def test_app_call_command_status_update(self):
        self.app.bg_update = True
        self.app.notify_by_email = True
        # Set some invalid url to get a 404
        self.app.url += '/ht/'
        self.app.save()
        self.app.refresh_from_db()
        call_command('status_update')
        self.app.refresh_from_db()
        self.assertEqual(self.app.http_status, 404)
        self.assertEqual(self.app.last_update.date(), now().date())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, f'Monitoring Alert: {self.app.name}'
        )
        message = _(
            'Please check service {name} at {url}.'
        ).format(
            name=self.app.name,
            url=self.app.get_absolute_uri()
        )
        self.assertEqual(mail.outbox[0].body, message)
        self.assertTrue(self.app.alert_sent)

    def test_app_call_command_status_update_no_email(self):
        self.app.bg_update = True
        self.app.notify_by_email = False
        # Set some invalid url to get a 404
        self.app.url += '/ht/'
        self.app.save()
        self.app.refresh_from_db()
        call_command('status_update')
        self.app.refresh_from_db()
        self.assertEqual(self.app.http_status, 404)
        self.assertEqual(self.app.last_update.date(), now().date())
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(self.app.alert_sent)

    def test_app_call_command_status_update_not_sent_twice(self):
        self.app.bg_update = True
        # Set some invalid url to get a 404
        self.app.url += '/ht/'
        self.app.alert_sent = True
        self.app.save()
        self.app.refresh_from_db()
        call_command('status_update')
        self.app.refresh_from_db()
        self.assertEqual(self.app.http_status, 404)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(self.app.alert_sent)

    def test_app_call_command_truncate_metrics(self):
        # Create some stale metrics, which will be deleted
        for i in range(5):
            SystemMetric.objects.create(
                app=self.app,
                cpu_percent=i*0.3,
                mem_percent=i*0.2,
            )
            day_before = now() - timedelta(days=1)
            SystemMetric.objects.update(
                timestamp=day_before
            )
        # Create some current metrics, which will not be deleted
        for i in range(3):
            SystemMetric.objects.create(
                app=self.app,
                cpu_percent=i*0.1,
                mem_percent=i*0.4,
            )
        self.assertEqual(self.app.metrics.count(), 8)
        call_command('truncate_metrics')
        self.assertEqual(self.app.metrics.count(), 3)

    def test_application_list(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('app:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('app/application_list.html')
        self.assertQuerySetEqual(
            response.context['application_list'],
            Application.objects.all(),
        )

    def test_application_detail(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('app:detail', kwargs={'pk': self.app.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('app/application_detail.html')
        self.assertEqual(response.context['application'], self.app)

    def test_application_immedeate_update_view(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('app:update', kwargs={'app_id': self.app.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('app:list'))
