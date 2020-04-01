from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic.base import View
from django.utils.translation import ugettext_lazy as _

from devicedata.providers.opsi import OpsiProvider
from devicedata.providers.puppet import PuppetProvider
from devices.models import Device
import logging

data_providers = {
    "opsi": OpsiProvider,
    "puppet": PuppetProvider
}

logger = logging.getLogger(__name__)


def _get_provider(device):
    if device.data_provider is not None and device.data_provider in data_providers.keys():
        return data_providers[device.data_provider]()
    else:
        for provider in data_providers.values():
            provider_instance = provider()
            if provider_instance.has_device(device):
                return provider_instance


class DeviceDetails(View):

    @staticmethod
    def get(request, device):
        device = get_object_or_404(Device, pk=device)
        try:
            device_info = _get_provider(device).get_device_info(device)
        except Exception as e:
            logger.error(e)
            return HttpResponse(_("Could not load data."))
        context = {
            'device_info': device_info.raw_entries
        }
        return render(request, 'devicedata/device_info.html', context)


class DeviceDetailsJson(View):

    @staticmethod
    def get(request, device):
        device = get_object_or_404(Device, pk=device)
        provider = _get_provider(device)
        if provider is None:
            return JsonResponse({})
        device_info = provider.get_device_info(device)
        raw_entries = [{"name": entry.name,
                        "type": entry.type,
                        "raw_value": entry.raw_value} for entry in device_info.raw_entries]
        formatted_entries = [{"name": entry.name,
                              "value": entry.value} for entry in device_info.formatted_entries]
        return JsonResponse({"raw_entries": raw_entries, "formatted_entries": formatted_entries})


class DeviceSoftware(View):

    @staticmethod
    def get(request, device):
        device = get_object_or_404(Device, pk=device)
        try:
            software_info = _get_provider(device).get_software_info(device)
        except Exception as e:
            logger.error(e)
            return HttpResponse(_("Could not load data."))
        context = {
            'software_info': software_info
        }
        return render(request, 'devicedata/software_info.html', context)
