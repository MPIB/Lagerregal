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
        devices = Device.objects.filter(name__contains=" - ")
        for device in devices:
            old_name = device.name
            device.name = device.name.split(" - ")[0]
            device.save()
            print("Renamed", old_name, "to", device.name)
        devices = Device.objects.filter(name__regex=r'\([a-zA-Z0-9\s]{8,50}\)')
        for device in devices:
            old_name = device.name
            device.name = device.name.split(" (")[0]
            device.save()
            print("Renamed", old_name, "to", device.name)
