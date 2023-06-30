from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
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

    def test_app_get_status(self):
        self.assertEqual(self.app.get_status(), {'code': 404, 'text': 'Not Found'})

    def test_application_list(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('app:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('app/application_list.html')
        self.assertQuerySetEqual(
            response.context['application_list'],
            Application.objects.all(),
        )
        # We don't have a URL to test, so example.com will respond with 404
        self.assertEqual(response.context['application_list'][0].code, 404)

