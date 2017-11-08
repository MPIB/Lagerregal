import os.path


from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse

from locations.models import Section
from users.models import Lageruser


class SectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username = "test", password = "test")

    def test_section_creation(self):
        section = mommy.make(Section)
        self.assertEqual(section.__unicode__(), section.name)
        self.assertEqual(section.get_absolute_url(), reverse('section-detail', kwargs={'pk': section.pk}) )
        self.assertEqual(section.get_edit_url(), reverse('section-edit', kwargs={'pk': section.pk}))

    def test_section_list(self):
        section = mommy.make(Section, _quantity=40)
        url = reverse("section-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["section_list"]), 30)
        self.assertEqual(resp.context["paginator"].num_pages, 2)
        url = reverse("section-list", kwargs={"page": 2})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_section_detail(self):
        section = mommy.make(Section)
        sections = Section.objects.all()
        section = sections[0]
        url = reverse("section-detail", kwargs={"pk": section.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_section_add(self):
        section = mommy.make(Section)
        url = reverse("section-add")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_section_edit(self):
        section = mommy.make(Section)
        sections = Section.objects.all()
        section = sections[0]
        url = reverse("section-edit", kwargs={"pk": section.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_section_delete(self):
        section = mommy.make(Section)
        sections = Section.objects.all()
        section = sections[0]
        url = reverse("section-edit", kwargs={"pk": section.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
