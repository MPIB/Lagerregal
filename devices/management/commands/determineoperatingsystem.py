from django.conf import settings
from django.core.management import BaseCommand

from devices.models import Device

os_mapping = {
    "w7": "win",
    "w10": "win",
    "win7": "win",
    "win10": "win"
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        devices = Device.objects.exclude(hostname="").filter(operating_system__isnull=True, ipaddress__isnull=False)
        for device in devices:
            osname = device.hostname.split("-")[1]
            if osname in os_mapping:
                osname = os_mapping[osname]
            for entry in settings.OPERATING_SYSTEMS:
                if osname == entry[0]:
                    device.operating_system = osname
                    device.save()
                    print("Set", device, "to", osname)
                    continue
