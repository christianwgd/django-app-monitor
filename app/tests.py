from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.utils.timezone import now
from faker import Faker

from app.models import Application


User = auth.get_user_model()


class ApplicationTest(TestCase):

    def setUp(self):
        self.fake = Faker()
        Faker.seed(0)

        self.admin = User.objects.create(
            username=self.fake.user_name()
        )
        self.app = Application.objects.create(
            name=self.fake.word(),
            url='https://example.com',
        )
        self.app.admins.add(self.admin)

    def test_app_str(self):
        self.assertEqual(str(self.app), self.app.name)

    def test_app_get_http_status(self):
        self.assertEqual(self.app.get_http_status(), 200)

    def test_app_get_health_check_data(self):
        self.assertEqual(
            self.app.get_health_check_data(),
            {}
        )

    def test_app_update_status(self):
        self.app.bg_update = True
        self.app.save()
        self.app.refresh_from_db()
        self.app.update_status()
        self.assertEqual(self.app.http_status, 200)
        self.assertEqual(self.app.last_update.date(), now().date())

    def test_application_list(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('app:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('app/application_list.html')
        self.assertQuerySetEqual(
            response.context['application_list'],
            Application.objects.all(),
        )
