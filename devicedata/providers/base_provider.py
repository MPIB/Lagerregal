from devices.models import Device
from abc import ABC, abstractmethod


class BaseDeviceInfo(ABC):
    formatted_entries = []
    raw_entries = []

    def find_entries(self, entry_type):
        return [entry for entry in self.raw_entries if entry.type == entry_type]

    def __init__(self, raw_entries):
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
