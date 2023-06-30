from django.test import TestCase
from django.urls import reverse
from faker import Faker

from app.models import Application


class ApplicationTest(TestCase):

    def setUp(self):
        self.fake = Faker()
        Faker.seed(0)

        user
        self.app = Application.objects.create(
            name=self.fake.word(),
            url=self.fake.uri(),
        )

    def test_app_str(self):
        self.assertEqual(str(self.app), self.app.name)

    def test_application_list(self):
        response = self.client.get(reverse('app:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('app/application_list.html')
        self.assertQuerySetEqual(
            response.context['application_list'],
            Application.objects.all(),
        )

