from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from devices.models import Device, Room, Building, Manufacturer
from mail.models import MailTemplate
from django.shortcuts import get_object_or_404
from devicetypes.models import Type
from django.utils import simplejson
from django.core.urlresolvers import reverse
from devices.forms import AddForm
from dajaxice.utils import deserialize_form
from django.forms.models import modelform_factory
from django.template.loader import render_to_string
from django.template import Template, Context

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
        objects = ["<li><a href='{}'  class='alert-link'>{}</a></li>".format(
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
    dform = deserialize_form(form)
    classname = dform["classname"]
    if classname == "manufacturer":
        form = modelform_factory(Manufacturer, form=AddForm)(dform)
    elif classname == "devicetype":
        form = modelform_factory(Type, form=AddForm)(dform)
    elif classname == "room":
        form = modelform_factory(Room, form=AddForm)(dform)
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
            dajax.script("$('#addModal').modal('hide');")

    else:
        dajax.assign("#modal_errors", "innerHTML", "Error: {0}".format(form.non_field_errors()))

    return dajax.json()

@dajaxice_register
def load_extraform(request, classname):
    dajax = Dajax()
    if classname == "manufacturer":
        form = modelform_factory(Manufacturer, form=AddForm)()
    elif classname == "devicetype":
        form = modelform_factory(Type, form=AddForm)()
    elif classname == "room":
        form = modelform_factory(Room, form=AddForm)()

    dajax.assign("#modal-form", "innerHTML", render_to_string('snippets/formfields.html', {"form":form}))
    dajax.script("$('#addModal').modal('show');")
    return dajax.json()


@dajaxice_register
def load_mailpreview(request, template, device, owner=None):
    dajax = Dajax()
    if template == "":
        return dajax.json()

    if device["manufacturer"] != "":
        device["manufacturer"] = get_object_or_404(Manufacturer, pk=device["manufacturer"])
    else:
        del device["room"]

    if device["devicetype"] != "":
        device["devicetype"] = get_object_or_404(Type, pk=device["devicetype"])
    else:
        del device["devicetype"]

    if device["room"] != "":
        device["room"] = get_object_or_404(Room, pk=device["room"])
    else:
        del device["room"]

    device = Device(**device)
    template = get_object_or_404(MailTemplate, pk=template)
    rendered_template  = Template(template.body).render(Context({"device":device, "user":request.user}))
    dajax.assign("#previewModalSubject", "innerHTML", template.subject)
    dajax.assign("#previewModalBody", "innerHTML", rendered_template.replace("\n", "<br />"))
    dajax.script("$('#previewModal').modal('show');")
    return dajax.json()

@dajaxice_register
def load_mailtemplate(request, template, fieldtype=None):
    dajax = Dajax()
    if template == "":
        return dajax.json()
    template = get_object_or_404(MailTemplate, pk=template)

    if fieldtype == None:
        dajax.assign("#id_emailsubject", "value", template.subject)
    else:
        dajax.assign("#id_emailsubject_{}".format(fieldtype), "value", template.subject)
    

    if fieldtype == None:
        dajax.assign("#id_emailbody", "innerHTML", template.body)
    else:
        dajax.assign("#id_emailbody_{}".format(fieldtype), "innerHTML", template.body)
    return dajax.json()