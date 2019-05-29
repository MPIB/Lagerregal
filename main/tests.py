from django.test import TestCase
from django.test.client import Client

from main.models import get_progresscolor
from users.models import Lageruser


class TestMethods(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_progresscolor(self):
        self.assertEqual(get_progresscolor(91), "danger")
        self.assertEqual(get_progresscolor(90), "warning")
        self.assertEqual(get_progresscolor(59), "success")

    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
