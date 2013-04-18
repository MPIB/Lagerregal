"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import unittest
from django.test.client import Client
from models import Device

class DeviceTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username="testuser", password="test")

    def test_list(self):
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['device_list']), 6)

    def test_add(self):
        response = self.client.post('/devices/add', {
              "name": "test",
              "buildnumber":"1",
              "serialnumber":"15",
              "macaddress":"36",
              "hostname":"1236",
              "devicetype":"3",
              "room":"3",
              "manufacturer":"3"
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['device_list']), 7)

        Device.objects.get(pk=7).delete()
        
