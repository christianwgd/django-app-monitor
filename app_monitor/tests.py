from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from faker import Faker

from app_monitor.utils import get_client_ip


class AppMonitorTestCase(TestCase):

    def setUp(self):
        self.fake = Faker()
        Faker.seed(0)
        self.factory = RequestFactory()

    def test_get_client_ip(self):
        request = self.factory.get(reverse('home'))
        # For local call result is always None
        self.assertIsNone(get_client_ip(request))
