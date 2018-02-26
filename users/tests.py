from __future__ import unicode_literals
import os.path


from django.test.client import Client
from django.test import TestCase
from model_mommy import mommy
from django.core.urlresolvers import reverse


from users.models import Lageruser, Department

class LageruserTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser('test', "test@test.com", "test")
        self.client.login(username = "test", password = "test")

    def test_lageruser_creation(self):
        user1 = mommy.make(Lageruser, first_name = "a", last_name = "a")
        user2 = mommy.make(Lageruser, first_name = "", last_name = "a")
        self.assertEqual(user1.__unicode__(), u"{0} {1}".format(user1.first_name, user1.last_name) )
        self.assertEqual(user2.__unicode__(), user2.username)
        self.assertEqual(user1.get_absolute_url(), reverse('userprofile', kwargs={'pk': user1.pk}) )
        user1.clean()
        self.assertEqual(user1.expiration_date, None)


class DepartmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        myadmin = Lageruser.objects.create_superuser('test', "test@test.com", "test")
        self.client.login(username = "test", password = "test")

    def test_department_creation(self):
        department = mommy.make(Department)
        self.assertEqual(department.__unicode__(), department.name)
