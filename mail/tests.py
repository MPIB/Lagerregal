import unittest

from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

import six
from model_mommy import mommy

from mail.models import MailTemplate, MailTemplateRecipient, MailHistory
from users.models import Lageruser


class TestMailTemplate(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_template_creation(self):
        template = mommy.make(MailTemplate)
        self.assertEqual(six.text_type(template), template.name)
        self.assertEqual(template.get_absolute_url(), reverse('mail-detail', kwargs={'pk': template.pk}))
        self.assertEqual(template.get_edit_url(), reverse('mail-edit', kwargs={'pk': template.pk}))


class TestMailTemplateRecipient(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    @unittest.skip("first figuring out strange behaviour of content_object")
    def test_template_creation(self):
        con = mommy.make(ContentType)
        rec = mommy.make(MailTemplateRecipient, content_type=con)
        self.assertEqual(six.text_type(rec), six.text_type(rec.content_type.name + ": " + six.text_type(rec.content_object)))


class TestMailHistory(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username="test", password="test")

    @unittest.skip("find out why url does not exist")
    def test_mail_history_creation(self):
        hist = mommy.make(MailHistory)
        self.assertEqual(hist.get_absolute_url(), reverse('mailhistory-detail', kwargs={'pk': hist.pk}))
