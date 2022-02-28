import base64
from unicodedata import name

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

import requests

from devicedata.providers.base_provider import BaseDeviceInfo
from devicedata.providers.base_provider import BaseProvider
from devicedata.providers.base_provider import DeviceInfoEntry
from devicedata.providers.base_provider import FormattedDeviceInfoEntry
from devicedata.providers.helpers import format_bytes


class BaramundiDeviceInfo(BaseDeviceInfo):
    def format_serialnumber(self):
        self.simple_format('SerialNumber', _('Serial Number'))

    def format_hostname(self):
        self.simple_format('HostName', _('Hostname'))

    def format_type(self):
        self.simple_format('ModelName', _('Type'))

    def format_lastseen(self):
        self.simple_format('LastSeen', _('Last Seen'))

    def format_processor(self):
        self.simple_format('CPUDescription', _('Processor'))

    def format_memory(self):
        entries = self.find_entries("TotalMemory")
        if len(entries) > 0:
            self.formatted_entries.append(
                FormattedDeviceInfoEntry(_("Memory"), format_bytes(entries[0].raw_value * 1024 * 1024)))

    def format_storage(self):
        entries = self.find_entries("StorageMedia")
        drives = []
        for entry in entries:
            for disk in entry.raw_value:
                if "ByteSize" in disk and disk["ByteSize"] < 1000000000:
                    # Smaller than 10gb. This most likely is not a hard drive.
                    continue
                drives.append(disk)
        formatted_capacities = "<br />".join(
            ["{0}: {1}".format(drive["Name"], format_bytes(drive["ByteSize"])) for drive in drives])
        self.formatted_entries.append(FormattedDeviceInfoEntry(_("Storage"), formatted_capacities))

    def format_entries(self):
        self.format_serialnumber()
        self.format_hostname()
        self.format_lastseen()
        self.format_processor()
        self.format_memory()
        self.format_storage()

class BaramundiProvider(BaseProvider):
    name = "baramundi"

    @staticmethod
    def __run_query(url):
        if not hasattr(settings, "BARAMUNDI_SETTINGS"):
            return
        
        host = settings.BARAMUNDI_SETTINGS['host'] + ":" + str(settings.BARAMUNDI_SETTINGS['port'])
        full_url = url %host
        if 'authorization' in settings.BARAMUNDI_SETTINGS:
            authorization = settings.BARAMUNDI_SETTINGS['authorization']
        else:
            authorization = ('{}:{}'.format(settings.BARAMUNDI_SETTINGS['user_name'], settings.BARAMUNDI_SETTINGS['password'])).encode('ascii')
            authorization = base64.b64encode(authorization).decode('ascii')
        session = requests.Session()
        session.headers.update({'Authorization': 'Basic {}'.format(authorization), 'content-type': "application/json; charset=utf-8"})

        print(full_url, settings.BARAMUNDI_SETTINGS['ignore_ssl'] is not True)
        result = session.get(full_url, verify=settings.BARAMUNDI_SETTINGS['ignore_ssl'] is not True)
        body = result.json()
        if len(body) == 0:
            raise ObjectDoesNotExist()
        return body

    def _get_device_id(self, device):
        if len(device.hostname) > 0:
            term = device.hostname
        else:
            term = '{:06d}'.format(device.id)
        try:
            data = self.__run_query('https://%s/bConnect/v1.0/search.json?type=endpoint&term=' + term)
            print(data)
            return data[0]['Id']
        except ObjectDoesNotExist:
            print("no object")
            return None
        except KeyError as e:
            print(e)
            return None

    def get_device_info(self, device):
        if not hasattr(settings, "BARAMUNDI_SETTINGS"):
            return
        id = self._get_device_id(device)
        if id is None:
            return
        info = self.__run_query('https://%s/bConnect/v1.0/endpoints.json?id=' + id)
        device_entries = []
        for key in info:
            device_entries.append(DeviceInfoEntry(key, None, info[key]))
        return BaramundiDeviceInfo(device, device_entries)

    def get_software_info(self, device):
        return
        if not hasattr(settings, "BARAMUNDI_SETTINGS"):
            return
        id = self._get_device_id(device)
        if id is None:
            return
        info = self.__run_query('https://%s/bConnect/v1.0/softwarescanrules.json?id=' + id)
        print(info)
        return super().get_software_info(device)

    def has_device(self, device):
        if not hasattr(settings, "BARAMUNDI_SETTINGS"):
            return False
        try:
            id = self._get_device_id(device)
            print(id)
            return id is not None and len(id) > 0
        except ObjectDoesNotExist:
            return False