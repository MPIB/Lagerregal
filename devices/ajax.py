from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from devices.models import *
from django.utils import simplejson

@dajaxice_register
def complete_devicenames(request, name):
	devices = Device.objects.filter(name__icontains = name )[:20]
	results = []
	for device in devices:
		device_json = {}
		device_json['id'] = device.pk
		device_json['label'] = device.name
		device_json['value'] = device.name
		results.append(device_json)
	return  simplejson.dumps(results)
	
@dajaxice_register
def complete_names(request, classtype, name):	
	if classtype == "type":
		objects = Type.objects.filter(name__icontains = name )[:20]
		urlname = "type-detail"
	elif classtype == "room":
		objects = Room.objects.filter(name__icontains = name )[:20]
		urlname = "room-detail"
	elif classtype == "building":
		objects = Building.objects.filter(name__icontains = name )[:20]
		urlname = "building-detail"
	elif classtype == "manufacturer":
		objects = Manufacturer.objects.filter(name__icontains = name )[:20]
		urlname = "manufacturer-detail"
	else:
		return None
	dajax = Dajax()
	if len(objects) > 0:
		objects = ["<li><a href='{}' style='color:white'>{}</a></li>".format(reverse(urlname, kwargs={"pk":object[0]}), object[1]) 
			for object in objects.values_list("pk", "name")]
		print objects
		dajax.add_data(objects, 'display_alternatives')
		return dajax.json()
	else:
		dajax.remove("#alternativebox")
		return dajax.json()