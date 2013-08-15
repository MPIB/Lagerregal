from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from devices.models import Device, Room, Building, Manufacturer
from devicetypes.models import Type
from django.utils import simplejson
from django.core.urlresolvers import reverse
from devices.forms import AddForm
from dajaxice.utils import deserialize_form

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
        objects = ["<li><a href='{}' style='color:white'>{}</a></li>".format(
		reverse(urlname, kwargs={"pk":object[0]}), object[1])
		for object in objects.values_list("pk", "name")]
        dajax.add_data(objects, 'display_alternatives')
        return dajax.json()
    else:
        dajax.remove("#alternativebox")
        return dajax.json()


@dajaxice_register
def add_device_field(request, form):
    dajax = Dajax()
    form = AddForm(deserialize_form(form))
    if form.is_valid():
        if request.user.is_staff:
            classname = form.cleaned_data["classname"]
            if classname == "manufacturer":
                newitem = Manufacturer()
                newitem.name = form.cleaned_data["name"]
                newitem.save()
            elif classname == "devicetype":
                newitem = Type()
                newitem.name = form.cleaned_data["name"]
                newitem.save()
            elif classname == "room":
                newitem = Room()
                newitem.name = form.cleaned_data["name"]
                newitem.save()
            dajax.append("#id_{0}".format(classname), 
                "innerHTML", 
                "<option value='{0}''>{1}</option>".format(newitem.pk, newitem.name))
            dajax.script("$('#id_{0}').select2('val', '{1}');".format(classname, newitem.pk))
            dajax.script("$('#addModal').foundation('reveal', 'close');")

    else:
        dajax.assign("#modal_errors", "innerHTML", "Error: {0}".format(form.non_field_errors()))

    return dajax.json()