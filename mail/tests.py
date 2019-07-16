from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from model_mommy import mommy

from mail.models import MailTemplate
from users.models import Lageruser


class TestMailTemplate(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_template_creation(self):
        template = mommy.make(MailTemplate)
        self.assertEqual(str(template), template.name)
        self.assertEqual(template.get_absolute_url(), reverse('mail-detail', kwargs={'pk': template.pk}))
        self.assertEqual(template.get_edit_url(), reverse('mail-edit', kwargs={'pk': template.pk}))

    def test_list_view(self):
        response = self.client.get('/mails/')
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/mails/add/')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        template = mommy.make(MailTemplate)
        response = self.client.get('/mails/%i/' % template.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        template = mommy.make(MailTemplate)
        response = self.client.get('/mails/%i/edit/' % template.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        template = mommy.make(MailTemplate)
        response = self.client.get('/mails/%i/delete/' % template.pk)
        self.assertEqual(response.status_code, 200)
