from django.test import TestCase

from main.models import get_progresscolor


class TestMethods(TestCase):
    def test_progresscolor(self):
        self.assertEqual(get_progresscolor(91), "danger")
        self.assertEqual(get_progresscolor(90), "warning")
        self.assertEqual(get_progresscolor(59), "success")
