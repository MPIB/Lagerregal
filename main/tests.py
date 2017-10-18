import os.path


from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from main.models import get_progresscolor
from users.models import Lageruser



class TestMethods(TestCase):
    def test_progresscolor(self):
        self.assertEqual(get_progresscolor(91), "danger")
        self.assertEqual(get_progresscolor(90), "warning")
        self.assertEqual(get_progresscolor(59), "success")
