from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from devicedata.providers.base_provider import BaseDeviceInfo
from devicedata.providers.base_provider import BaseProvider
from devicedata.providers.base_provider import DeviceInfoEntry
from devicedata.providers.base_provider import FormattedDeviceInfoEntry
from devicedata.providers.base_provider import SoftwareEntry
from devicedata.providers.base_provider import build_full_hostname
from devicedata.providers.helpers import format_bytes
from devicedata.providers.opsirpc import OpsiConnection


class OpsiDeviceInfo(BaseDeviceInfo):

    def format_chassis(self):
        entries = self.find_entries("CHASSIS")
        if len(entries) > 0:
            self.formatted_entries.append(
                FormattedDeviceInfoEntry(_("Serial Number"), entries[0].raw_value["serialNumber"]))
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Type"), entries[0].raw_value["chassisType"]))

    def format_system(self):
        entries = self.find_entries("COMPUTER_SYSTEM")
        if len(entries) > 0:
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Manufacturer"), entries[0].raw_value["vendor"]))
            hostname = build_full_hostname(self.device)
            if entries[0].raw_value["hostId"] != hostname:
                self.formatted_entries.append(FormattedDeviceInfoEntry(_("Hostname"), "<span class='text-warning'>"
                                                                       + entries[0].raw_value["hostId"] + "</span>"))
            else:
                self.formatted_entries.append(FormattedDeviceInfoEntry(_("Hostname"), entries[0].raw_value["hostId"]))
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Last Seen"), entries[0].raw_value["lastseen"]))

    def format_processor(self):
        entries = self.find_entries("PROCESSOR")
        if len(entries) > 0:
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Processor"), entries[0].name))

    def format_memory(self):
        entries = self.find_entries("MEMORY_MODULE")
        capacities = []
        for entry in entries:
            capacities.append(entry.raw_value["capacity"])
        total_capacity = format_bytes(sum(capacities))
        formatted_capacities = ", ".join([format_bytes(capacity) for capacity in capacities])
        self.formatted_entries.append(
            FormattedDeviceInfoEntry(_("Memory"), "{0} ({1})".format(total_capacity, formatted_capacities)))

    def format_storage(self):
        entries = self.find_entries("HARDDISK_DRIVE")
        drives = []
        for entry in entries:
            if "USB" not in entry.raw_value["name"]:
                drives.append(entry.raw_value)
        formatted_capacities = "<br />".join(
            ["{0} {1}".format(drive["model"], format_bytes(drive["size"], power=1000)) for drive in drives])
        self.formatted_entries.append(FormattedDeviceInfoEntry(_("Storage"), formatted_capacities))

    def format_network(self):
        entries = self.find_entries("NETWORK_CONTROLLER")
        controllers = []
        for entry in entries:
            if entry.raw_value["ipAddress"] is not None:
                controllers.append(entry.raw_value)
        formatted_controllers = []
        device_addresses = self.device.ipaddress_set.all()
        for controller in controllers:
            if any(elem.address in controller["ipAddress"] for elem in device_addresses):
                formatted_controllers.append("{0} {1}".format(controller["description"], controller["ipAddress"]))
            else:
                formatted_controllers.append(
                    "{0} <span class='text-warning'>{1}<span>".format(controller["description"],
                                                                      controller["ipAddress"]))
        self.formatted_entries.append(FormattedDeviceInfoEntry(_("Network"), "<br />".join(formatted_controllers)))

    def format_graphics(self):
        entries = self.find_entries("VIDEO_CONTROLLER")
        if len(entries) > 0:
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Graphics"), entries[0].name))

    def format_entries(self):
        self.format_chassis()
        self.format_system()
        self.format_processor()
        self.format_memory()
        self.format_storage()
        self.format_network()
        self.format_graphics()


class OpsiProvider(BaseProvider):
    name = "opsi"

    def __init__(self):
        self.__connection = OpsiConnection(
            settings.OPSI_SETTINGS["host"] + ":" + settings.OPSI_SETTINGS["port"],
            username=settings.OPSI_SETTINGS["username"],
            password=settings.OPSI_SETTINGS["password"],
            legal_methods_path="devicedata/providers/rpc_methods.txt",
        )

    def __get_host(self, device):
        host = None
        hostname = build_full_hostname(device)
        if len(hostname) > 0:
            response = self.__connection.host_getObjects(id=hostname)
            if len(response) == 1:
                return response[0]
        for ip in device.ipaddress_set.all():
            response = self.__connection.host_getObjects(ipAddress=ip.address)
            for h in response:
                host = h
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
        return OpsiDeviceInfo(device, device_entries)

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
