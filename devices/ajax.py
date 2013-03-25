from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from devices.models import Device 
from django.utils import simplejson

@dajaxice_register
def complete_devicenames(request, name):
	print name
	devices = Device.objects.filter(name__icontains = name )[:20]
	results = []
	for device in devices:
		device_json = {}
		device_json['id'] = device.pk
		device_json['label'] = device.name
		device_json['value'] = device.name
		results.append(device_json)
	return  simplejson.dumps(results)