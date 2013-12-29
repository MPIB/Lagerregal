# -*- coding: utf-8 -*-
from devices.models import Device, Room, Building, Manufacturer
from mail.models import MailTemplate
from django.shortcuts import get_object_or_404
from devicetypes.models import Type
from django.utils import simplejson
from django.core.urlresolvers import reverse
from devices.forms import AddForm
from django.forms.models import modelform_factory
from django.template.loader import render_to_string
from django.template import Template, Context
from devicegroups.models import Devicegroup
from django.views.generic.base import View
from django.http import HttpResponse
import pystache
from django.http import QueryDict

class AutocompleteDevice(View):
    def post(self, request):
        name = request.POST["name"]
        devices = Device.objects.filter(name__icontains = name )[:20]
        results = []
        for device in devices:
            device_json = {}
            device_json['id'] = device.pk
            device_json['label'] = device.name
            device_json['value'] = device.name
            results.append(device_json)
        return HttpResponse(simplejson.dumps(results), content_type='application/json')


class AutocompleteName(View):
    def post(self, request):
        name = request.POST["name"]
        classtype = request.POST["classtype"]
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
            return HttpResponse("")
        if len(objects) > 0:
            retobjects = ["<li><a href='{0}'  class='alert-link'>{1}</a></li>".format(
                reverse(urlname, kwargs={"pk":obj[0]}), obj[1])
                for obj in objects.values_list("pk", "name")]
            return HttpResponse(simplejson.dumps(retobjects), content_type='application/json')
        else:
            return HttpResponse("")


class AddDeviceField(View):
    def post(self, request):
        dform = QueryDict(query_string=unicode(request.POST["form"]).encode('utf-8'))
        classname = dform["classname"]
        if classname == "manufacturer":
            form = modelform_factory(Manufacturer, form=AddForm)(dform)
        elif classname == "devicetype":
            form = modelform_factory(Type, form=AddForm)(dform)
        elif classname == "room":
            form = modelform_factory(Room, form=AddForm)(dform)
        elif classname == "group":
            form = modelform_factory(Devicegroup, form=AddForm)(dform)
        else:
            return HttpResponse("")
        data = {}
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
                elif classname == "group":
                    newitem = Devicegroup()
                    newitem.name = form.cleaned_data["name"]
                    newitem.save()
                data["id"] = newitem.pk
                data["name"] = newitem.name
                data["classname"] = classname
        else:
            data["error"] = "Error: {0}".format(form.non_field_errors())
        return HttpResponse(simplejson.dumps(data), content_type='application/json')


class LoadExtraform(View):
    def post(self, request):
        classname = request.POST["classname"]
        if classname == "manufacturer":
            form = modelform_factory(Manufacturer, form=AddForm)()
        elif classname == "devicetype":
            form = modelform_factory(Type, form=AddForm)()
        elif classname == "room":
            form = modelform_factory(Room, form=AddForm)()
        elif classname == "group":
            form = modelform_factory(Devicegroup, form=AddForm)()
        else:
            return HttpResponse("")

        return HttpResponse(render_to_string('snippets/formfields.html', {"form":form}))


class PreviewMail(View):
    def post(self, request):
        print request.POST
        template = request.POST["template"]
        device = {
            "currentlending": request.POST.get("device[currentlending]", ""),
            "description": request.POST.get("device[description]", ""),
            "devicetype": request.POST.get("device[devicetype]", ""),
            "group": request.POST.get("device[group]", ""),
            "hostname": request.POST.get("device[hostname]", ""),
            "inventorynumber": request.POST.get("device[inventorynumber]", ""),
            "macaddress": request.POST.get("device[macaddress]", ""),
            "manufacturer": request.POST.get("device[manufacturer]", ""),
            "name": request.POST.get("device[name]", ""),
            "room": request.POST.get("device[room]", "") ,
            "serialnumber": request.POST.get("device[serialnumber]", ""),
            "templending": request.POST.get("device[templending]", ""),
            "webinterface": request.POST.get("device[webinterface]", "")
        }
        print device
        if template == "":
            return dajax.json()

        if device["manufacturer"] != "":
            device["manufacturer"] = get_object_or_404(Manufacturer, pk=device["manufacturer"])
        else:
            del device["manufacturer"]

        if device["devicetype"] != "":
            device["devicetype"] = get_object_or_404(Type, pk=device["devicetype"])
        else:
            del device["devicetype"]

        if device["room"] != "":
            device["room"] = get_object_or_404(Room, pk=device["room"])
        else:
            del device["room"]

        template = get_object_or_404(MailTemplate, pk=template)
        datadict = {}
        datadict["device"] = device
        datadict["user"] = {
            "username" : request.user.username,
            "first_name" : request.user.first_name,
            "last_name" : request.user.last_name
        }
        data = {}
        data["subject"] = pystache.render(template.subject, datadict)
        data["body"] = pystache.render(template.body, datadict).replace("\n", "<br />")
        return HttpResponse(simplejson.dumps(data), content_type='application/json')

class LoadMailtemplate(View):
    def post(self, request):
        template = request.POST["template"]
        recipients = request.POST.get("recipients[]", [])
        if template == "":
            return HttpResponse("")
        template = get_object_or_404(MailTemplate, pk=template)
        data = {}
        data["subject"] = template.subject
        data["body"] = template.body
        if isinstance(recipients, unicode):
            recipients = [recipients]
        newrecipients = [obj for obj in recipients]
        newrecipients += [obj.content_type.name[0].lower()+str(obj.object_id) for obj in template.default_recipients.all()]
        newrecipients = list(set(newrecipients))
        data["recipients"] = newrecipients
        return HttpResponse(simplejson.dumps(data), content_type='application/json')