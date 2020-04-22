import http.client
import json
from http.client import ssl
import urllib
import requests
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from Lagerregal import settings
from devicedata.providers.base_provider import BaseProvider, BaseDeviceInfo, DeviceInfoEntry, SoftwareEntry, \
    FormattedDeviceInfoEntry, build_full_hostname
from django.utils.translation import ugettext_lazy as _

from devicedata.providers.helpers import format_bytes


class PuppetDeviceInfo(BaseDeviceInfo):

    def format_serialnumber(self):
        entries = self.find_entries("sp_serial_number")
        entries.extend(self.find_entries("serialnumber"))
        if len(entries) > 0:
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Serial Number"), entries[0].raw_value))

    def format_type(self):
        entries = self.find_entries("sp_machine_name")
        if len(entries) > 0:
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Type"), entries[0].raw_value))

    def format_hostname(self):
        entries = self.find_entries("fqdn")
        if len(entries) > 0:
            hostname = build_full_hostname(self.device)
            if entries[0].raw_value["hostId"] != hostname:
                self.formatted_entries.append(FormattedDeviceInfoEntry(_("Hostname"), "<span class='text-warning'>" +
                                                                       entries[0].raw_value + "</span>"))
            else:
                self.formatted_entries.append(FormattedDeviceInfoEntry(_("Hostname"), entries[0].raw_value))

    def format_lastseen(self):
        entries = self.find_entries("timestamp")
        if len(entries) > 0:
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Last Seen"), entries[0].raw_value))

    def format_processor(self):
        entries = self.find_entries("processors")
        if len(entries) > 0:
            processors = {processor for processor in entries[0].raw_value["models"]}
            self.formatted_entries.append(
                FormattedDeviceInfoEntry(_("Processor"), "<br />".join(processors)))

    def format_memory(self):
        entries = self.find_entries("memory")
        if len(entries) > 0:
            system = entries[0].raw_value["system"]
            self.formatted_entries.append(
                FormattedDeviceInfoEntry(_("Memory"), format_bytes(system["total_bytes"])))

    def format_storage(self):
        entries = self.find_entries("disks")
        drives = []
        for entry in entries:
            for disk_identifier in entry.raw_value:
                disk = entry.raw_value[disk_identifier]
                if "size_bytes" in disk and disk["size_bytes"] < 1000000000:
                    # Smaller than 10gb. This most likely is not a hard drive.
                    continue
                if "model" in disk and "USB" not in disk["model"]:
                    disk["identifier"] = disk_identifier
                    drives.append(disk)
        formatted_capacities = "<br />".join(
            ["{0} ({1}): {2}".format(drive["model"], drive["identifier"], format_bytes(drive["size_bytes"])) for drive in drives])
        self.formatted_entries.append(FormattedDeviceInfoEntry(_("Storage"), formatted_capacities))

    def format_network(self):
        entries = self.find_entries("networking")
        controllers = []
        for entry in entries:
            interfaces = entry.raw_value["interfaces"]
            for interface in interfaces:
                if "mac" in interfaces[interface] and "ip" in interfaces[interface] and interfaces[interface]["mac"] is not None:
                    interfaces[interface]["identifier"] = interface
                    controllers.append(interfaces[interface])
        formatted_controllers = []
        device_addresses = self.device.ipaddress_set.all()
        for controller in controllers:
            if any(elem.address in controller["ipAddress"] for elem in device_addresses):
                formatted_controllers.append("{0} {1}".format(controller["identifier"], controller["ip"]))
            else:
                formatted_controllers.append(
                    "{0} <span class='text-warning'>{1}<span>".format(controller["identifier"], controller["ip"]))
        self.formatted_entries.append(FormattedDeviceInfoEntry(_("Network"), formatted_controllers))

    def format_graphics(self):
        entries = self.find_entries("VIDEO_CONTROLLER")
        if len(entries) > 0:
            self.formatted_entries.append(FormattedDeviceInfoEntry(_("Graphics"), entries[0].name))

    def format_entries(self):
        self.format_serialnumber()
        self.format_type()
        self.format_hostname()
        self.format_lastseen()
        self.format_processor()
        self.format_memory()
        self.format_storage()
        self.format_network()
        self.format_graphics()


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
        return PuppetDeviceInfo(device, device_entries)

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
