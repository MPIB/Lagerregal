from abc import ABC
from abc import abstractmethod

from Lagerregal import settings


class BaseDeviceInfo(ABC):
    device = None
    formatted_entries = []
    raw_entries = []

    def find_entries(self, entry_type):
        return [entry for entry in self.raw_entries if entry.type == entry_type]

    def __init__(self, device, raw_entries):
        self.device = device
        self.formatted_entries = []
        self.raw_entries = raw_entries
        self.format_entries()

    @abstractmethod
    def format_entries(self):
        pass


class FormattedDeviceInfoEntry:
    name = ""
    value = ""

    def __init__(self, name, value):
        self.name = name
        self.value = value


class DeviceInfoEntry:
    type = ""
    name = ""
    raw_value = {}

    def __init__(self, type, name, raw_value):
        self.type = type
        self.name = name
        self.raw_value = raw_value


class SoftwareEntry:
    name = ""
    version = ""

    def __init__(self, name, version):
        self.name = name
        self.version = version


class BaseProvider(ABC):

    @abstractmethod
    def get_device_info(self, device):
        pass

    @abstractmethod
    def get_software_info(self, device):
        pass

    @abstractmethod
    def has_device(self, device):
        pass


def build_full_hostname(device):
    hostname = device.hostname.lower()
    if len(hostname) > 0:
        if hasattr(settings, "HOST_BASE_DOMAIN") and not hostname.endswith(
                settings.HOST_BASE_DOMAIN):
            hostname += "." + settings.HOST_BASE_DOMAIN
    return hostname
