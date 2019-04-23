from django.test.client import Client
from django.test import TestCase
from django.urls import reverse

from model_mommy import mommy

from devicetags.models import Devicetag
from users.models import Lageruser


class DevitagsTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', 'test@test.com', 'test')
        self.client.login(username='test', password='test')

    def test_devicetag_creation(self):
        tag = mommy.make(Devicetag)
        self.assertEqual(str(tag), tag.name)
        # there is no devicetag detail view
        self.assertEqual(tag.get_absolute_url(), reverse('devicetag-edit', kwargs={'pk': tag.pk}))
        self.assertEqual(tag.get_edit_url(), reverse('devicetag-edit', kwargs={'pk': tag.pk}))
