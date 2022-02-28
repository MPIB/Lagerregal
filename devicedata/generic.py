from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string

from devicedata.models import ProvidedData


def _get_provider(device):
    if device.data_provider in settings.DATA_PROVIDERS:
        provider_path = settings.DATA_PROVIDERS[device.data_provider]
        return import_string(provider_path)()
    else:
        for provider_path in settings.DATA_PROVIDERS.values():
            provider_instance = import_string(provider_path)()
            if provider_instance.has_device(device):
                return provider_instance


def _update_provided_data(device, data, force=False):
    old_data = device.provided_data.all()
    if not force:
        if len(old_data) > 0:
            if (timezone.now() - old_data[0].stored_at).days < 7:
                return old_data
    old_data.delete()
    for entry in data.formatted_entries:
        pd = ProvidedData()
        pd.device = device
        pd.name = entry.name
        pd.formatted_value = entry.value
        pd.save()
    return device.provided_data.all()
