from django.test import TestCase
from faker import Faker

from app.models import Application


class AppModelTest(TestCase):

    def setUp(self):
        self.fake = Faker()
        Faker.seed(0)

        self.app = Application.objects.create(
            name=self.fake.word(),
            url=self.fake.uri(),
        )


    def test_app_str(self):
        self.assertEqual(str(self.app), self.app.name)
