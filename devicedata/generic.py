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
