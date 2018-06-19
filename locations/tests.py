from __future__ import unicode_literals

from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse

import six
from model_mommy import mommy

from locations.models import Section
from users.models import Lageruser


class SectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_section_creation(self):
        section = mommy.make(Section)
        self.assertEqual(six.text_type(section), section.name)
        self.assertEqual(section.get_absolute_url(), reverse('section-detail', kwargs={'pk': section.pk}))
        self.assertEqual(section.get_edit_url(), reverse('section-edit', kwargs={'pk': section.pk}))
