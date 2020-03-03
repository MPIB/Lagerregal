import http.client
import json
from http.client import ssl
import urllib
import requests
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.http import HttpResponse
from urllib3.exceptions import SubjectAltNameWarning

from Lagerregal import settings
from devicedata.providers.base_provider import BaseProvider, DeviceInfoEntry, SoftwareEntry


class PuppetProvider(BaseProvider):

    @staticmethod
    def __run_query(query):
        params = urllib.parse.urlencode({'query': query})

        if settings.PUPPETDB_SETTINGS['ignore_ssl'] is not True:
            context = ssl.create_default_context(cafile=settings.PUPPETDB_SETTINGS['cacert'])
            context.load_cert_chain(
                certfile=settings.PUPPETDB_SETTINGS['cert'],
                keyfile=settings.PUPPETDB_SETTINGS['key'],
            )
            conn = http.client.HTTPSConnection(
                settings.PUPPETDB_SETTINGS['host'],
                settings.PUPPETDB_SETTINGS['port'],
                context=context,
            )
            conn.request("GET", settings.PUPPETDB_SETTINGS['req'] + params)
            res = conn.getresponse()
            if res is None or res.status != http.client.OK:
                raise ValidationError("Puppet")
            try:
                body = json.loads(res.read().decode())
            except:
                raise ValidationError("Puppet")
        else:
            host = settings.PUPPETDB_SETTINGS['host'] + ":" + str(settings.PUPPETDB_SETTINGS['port'])
            if "http" not in host:
                host = "http://" + host
            res = requests.get(host + settings.PUPPETDB_SETTINGS['req'] + params, verify=False)
            body = res.json()
        if len(body) == 0:
            raise ObjectDoesNotExist()
        return body

    def get_device_info(self, device):
        query = (
            '["in", "certname", ["extract", "certname", ["select_facts", '
            '["and", ["=", "name", "{}"], ["=", "value", "{}"]]]]]'
        ).format(settings.PUPPETDB_SETTINGS['query_fact'], str(device.id))
        res = self.__run_query(query)
        device_entries = []
        for entry in res:
            device_entries.append(DeviceInfoEntry(entry["name"], None, entry["value"]))
        return device_entries

    def get_software_info(self, device):
        software_fact = settings.PUPPETDB_SETTINGS['software_fact']
        query_fact = settings.PUPPETDB_SETTINGS['query_fact']

        query = (
            '["and", ["=", "name", "{}"], ["in", "certname", '
            '["extract", "certname", ["select_facts", ["and", '
            '["=", "name", "{}"], ["=", "value", "{}"]]]]]]'
        ).format(software_fact, query_fact, str(device.id))
        res = self.__run_query(query)[0]
        software_infos = []
        for software_entry in res:
            software_infos.append(SoftwareEntry(software_entry["name"], software_entry["version"]))
        return software_infos

    def has_device(self, device):
        query = (
            '["in", "certname", ["extract", "certname", ["select_facts", '
            '["and", ["=", "name", "{}"], ["=", "value", "{}"]]]]]'
        ).format(settings.PUPPETDB_SETTINGS['query_fact'], str(device.id))
        try:
            data = self.__run_query(query)
            return data is not None and len(data) > 0
        except ObjectDoesNotExist:
            return False
