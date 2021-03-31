from django.utils import timezone

from devicedata.models import ProvidedData
from devicedata.providers.opsi import OpsiProvider
from devicedata.providers.puppet import PuppetProvider

data_providers = {
    "opsi": OpsiProvider,
    "puppet": PuppetProvider
}


def _get_provider(device):
    if device.data_provider is not None and device.data_provider in data_providers.keys():
        return data_providers[device.data_provider]()
    else:
        for provider in data_providers.values():
            provider_instance = provider()
            if provider_instance.has_device(device):
                return provider_instance


def _update_provided_data(device, data, force=False):
    if not force:
        old_data = device.provided_data.all()
        if len(old_data) > 0:
            if (timezone.now() - old_data[0].stored_at).days < 7:
                return old_data
    device.provided_data.all().delete()
    for entry in data.formatted_entries:
        pd = ProvidedData()
        pd.device = device
        pd.name = entry.name
        pd.formatted_value = entry.value
        pd.save()
    return device.provided_data.all()
