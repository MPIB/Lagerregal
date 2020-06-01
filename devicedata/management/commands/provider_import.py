from django.core.management import BaseCommand

from devicedata.generic import _get_provider
from devicedata.models import ProvidedData
from devices.models import Device
from datetime import datetime


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('device_ids', nargs='*', type=int)
        parser.add_argument('-f', '--force', action='store_true', dest='force')

    def handle(self, *args, **options):
        if "device_ids" in options and len(options["device_ids"]) > 0:
            devices = Device.objects.filter(pk__in=options["device_ids"])
        else:
            devices = Device.objects.exclude(data_provider__isnull=True)

        if len(devices) is 0:
            self.stdout.write("Could not find any devices with data provider.")
            return
        for device in devices:
            if not options["force"]:
                old_data = device.provided_data.all()
                if len(old_data) > 0:
                    if (datetime.now() - old_data[0].stored_at).days < 7:
                        continue

            self.stdout.write("Processing: {0} from {1}".format(device, device.data_provider))
            provider = _get_provider(device)
            if provider is None:
                continue
            data = provider.get_device_info(device)
            device.provided_data.all().delete()
            for entry in data.formatted_entries:
                pd = ProvidedData()
                pd.device = device
                pd.name = entry.name
                pd.formatted_value = entry.value
                pd.save()
