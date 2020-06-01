from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.timesince import timesince
from django.views.generic.base import View
from django.utils.translation import ugettext_lazy as _

from devicedata.generic import _get_provider, _update_provided_data
from devices.models import Device
import logging

from devices.templatetags.devicetags import as_nested_list

logger = logging.getLogger(__name__)


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
        _update_provided_data(device, device_info)
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
                        "raw_value": as_nested_list(entry.raw_value)} for entry in device_info.raw_entries]
        new_entries = _update_provided_data(device, device_info)
        formatted_entries = [{"name": entry.name,
                              "value": entry.formatted_value,
                              "stored_at": timesince(entry.stored_at)} for entry in new_entries]

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
