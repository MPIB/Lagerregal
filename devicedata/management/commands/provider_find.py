from django.core.management import BaseCommand

from devicedata.generic import _get_provider
from devices.models import Device


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('device_ids', nargs='*', type=int)

    def handle(self, *args, **options):
        if "device_ids" in options and len(options["device_ids"]) > 0:
            devices = Device.objects.filter(pk__in=options["device_ids"])
        else:
            devices = Device.objects.filter(data_provider="", ipaddress__isnull=False)

        if len(devices) == 0:
            self.stdout.write("Could not find any devices with data provider.")
            return
        for device in devices:
            provider = _get_provider(device)
            if provider is not None:
                device.data_provider = provider.name
                device.save()
                self.stdout.write("Processed: {0} with {1}".format(device, device.data_provider))
