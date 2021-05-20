from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from model_mommy import mommy

from locations.models import Section
from users.models import Lageruser


class SectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_section_creation(self):
        section = mommy.make(Section)
        self.assertEqual(str(section), section.name)
        self.assertEqual(section.get_absolute_url(), reverse('section-detail', kwargs={'pk': section.pk}))
        self.assertEqual(section.get_edit_url(), reverse('section-edit', kwargs={'pk': section.pk}))

    def test_list_view(self):
        response = self.client.get('/sections/')
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/sections/add/')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        section = mommy.make(Section)
        response = self.client.get('/sections/%i/' % section.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        section = mommy.make(Section)
        response = self.client.get('/sections/%i/edit/' % section.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        section = mommy.make(Section)
        response = self.client.get('/sections/%i/delete/' % section.pk)
        self.assertEqual(response.status_code, 200)

    def test_merge_view(self):
        section1 = mommy.make(Section)
        section2 = mommy.make(Section)
        response = self.client.get('/sections/%i/merge/%i/' % (section1.pk, section2.pk))
        self.assertEqual(response.status_code, 200)
