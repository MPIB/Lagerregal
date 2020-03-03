from django.core.exceptions import ObjectDoesNotExist

from Lagerregal import settings
from devicedata.providers.base_provider import BaseProvider, SoftwareEntry, DeviceInfoEntry
from devicedata.providers.opsirpc import OpsiConnection


class OpsiProvider(BaseProvider):
    __connection = OpsiConnection(settings.OPSI_SETTINGS["host"] + ":" + settings.OPSI_SETTINGS["port"],
                                  username=settings.OPSI_SETTINGS["username"],
                                  password=settings.OPSI_SETTINGS["password"],
                                  legal_methods_path="devicedata/providers/rpc_methods.txt")

    def __get_host(self, device):
        host = None
        for ip in device.ipaddress_set.all():
            response = self.__connection.host_getObjects(ipAddress=ip.address)
            host = response[0]
            for h in response:
                if str(device.id) in h['id']:
                    host = response[0]
                    break

        if host is None:
            raise ObjectDoesNotExist()
        return host

    def get_device_info(self, device):
        host = self.__get_host(device)
        hardware = self.__connection.auditHardwareOnHost_getObjects(hostId=host['id'])
        device_entries = []
        for entry in hardware:
            device_entries.append(DeviceInfoEntry(entry["hardwareClass"], entry["name"], entry))
        return device_entries

    def get_software_info(self, device):
        host = self.__get_host(device)
        software = self.__connection.auditSoftwareOnClient_getObjects(clientId=host['id'])
        software_infos = []
        for software_entry in software:
            software_infos.append(SoftwareEntry(software_entry["name"], software_entry["version"]))
        return software_infos

    def has_device(self, device):
        try:
            return self.__get_host(device) is not None
        except ObjectDoesNotExist:
            return False
