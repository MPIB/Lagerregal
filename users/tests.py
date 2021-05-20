from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from model_mommy import mommy

from users.models import Department
from users.models import DepartmentUser
from users.models import Lageruser


class LageruserTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_lageruser_creation(self):
        user1 = mommy.make(Lageruser, first_name="a", last_name="a")
        user2 = mommy.make(Lageruser, first_name="", last_name="a")
        self.assertEqual(str(user1), "{0} {1}".format(user1.first_name, user1.last_name))
        self.assertEqual(str(user2), user2.username)
        self.assertEqual(user1.get_absolute_url(), reverse('userprofile', kwargs={'pk': user1.pk}))
        user1.clean()
        self.assertEqual(user1.expiration_date, None)

    def test_list_view(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        user = mommy.make(Lageruser)
        response = self.client.get('/users/%i/' % user.pk)
        self.assertEqual(response.status_code, 200)

    def test_profile_view(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_settings_view(self):
        response = self.client.get('/settings/')
        self.assertEqual(response.status_code, 200)


class DepartmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        Lageruser.objects.create_superuser('test', "test@test.com", "test")
        self.client.login(username="test", password="test")

    def test_department_creation(self):
        department = mommy.make(Department)
        self.assertEqual(str(department), department.name)

    def test_list_view(self):
        response = self.client.get('/departments/')
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        response = self.client.get('/departments/add/')
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        department = mommy.make(Department)
        response = self.client.get('/departments/%i/' % department.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_view(self):
        department = mommy.make(Department)
        response = self.client.get('/departments/%i/edit/' % department.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        department = mommy.make(Department)
        response = self.client.get('/departments/%i/delete/' % department.pk)
        self.assertEqual(response.status_code, 200)

    def test_adduser_view(self):
        department = mommy.make(Department)
        response = self.client.get('/departments/%i/adduser/' % department.pk)
        self.assertEqual(response.status_code, 200)

    def test_removeuser_view(self):
        departmentuser = mommy.make(DepartmentUser)
        response = self.client.get('/departments/%i/removeuser/' % departmentuser.pk)
        self.assertEqual(response.status_code, 200)
