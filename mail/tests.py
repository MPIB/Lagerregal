import os.path


from django.test.client import Client, RequestFactory
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from mail.models import MailTemplate, MailTemplateRecipient, MailHistory
from devices.models import Device, Room, Building, Lending
from users.models import Lageruser




class TestMailTemplate(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
        self.client.login(username = "test", password = "test")

    def test_template_creation(self):
        template = mommy.make(MailTemplate)
        self.assertEqual(template.__unicode__(), template.name)
        self.assertEqual(template.get_absolute_url(), reverse('mail-detail', kwargs={'pk': template.pk}) )
        self.assertEqual(template.get_edit_url(), reverse('mail-edit', kwargs={'pk': template.pk}) )




#first figuring out strange behaviour of content_object
# class TestMailTemplateRecipient(TestCase):
#     def setUp(self):
#         self.client = Client()
#         myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
#         self.client.login(username = "test", password = "test")
#
#     def test_template_creation(self):
#         con = mommy.make(ContentType)
#         rec = mommy.make(MailTemplateRecipient, content_type = con)
#         self.assertEqual(rec.__unicode__(), unicode(rec.content_type.name + ": " + rec.content_object.__unicode__()))

#find out why url does not exist
# class TestMailHistory(TestCase):
#     def setUp(self):
#         self.client = Client()
#         myadmin = Lageruser.objects.create_superuser("test", "test@test.com", "test")
#         self.client.login(username = "test", password = "test")
#
#     def test_mail_history_creation(self):
#         hist = mommy.make(MailHistory)
#         self.assertEqual(hist.get_absolute_url(), reverse('mailhistory-detail', kwargs={'pk': hist.pk}) )
