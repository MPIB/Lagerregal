# -*- coding: utf-8 -*-
from devices.models import Device, Room, Building, Manufacturer
from devicetypes.models import Type
from devicegroups.models import Devicegroup
from users.models import Lageruser
from network.models import IpAddress
from mail.models import MailTemplate
from django.shortcuts import get_object_or_404
from devicetypes.models import Type
import json
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
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

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
        return HttpResponse(json.dumps(results), content_type='application/json')


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
            return HttpResponse(json.dumps(retobjects), content_type='application/json')
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
        return HttpResponse(json.dumps(data), content_type='application/json')


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
        if template == "":
            return HttpResponse("")

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
        return HttpResponse(json.dumps(data), content_type='application/json')

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
        return HttpResponse(json.dumps(data), content_type='application/json')

class LoadSearchoptions(View):
    def post(self, request):
        term = request.POST["searchTerm"]
        if term[:4] == "not ":
            term = term[4:]
            invert = True
        else:
            invert = False
        facet = request.POST["facet"]
        if facet == "manufacturer":
            items = Manufacturer.objects.filter(name__icontains=term)
        elif facet == "devicetype":
            items = Type.objects.filter(name__icontains=term)
        elif facet == "room":
            items = Room.objects.filter(name__icontains=term)
        elif facet == "devicegroup":
            items = Devicegroup.objects.filter(name__icontains=term)
        elif facet == "user":
            items = Lageruser.objects.filter(username__icontains=term)
        else:
            return HttpResponse("")
        if invert:
            data = [{"value": "not " + str(object.pk)+"-"+object.__unicode__(), "label" : "not " + object.__unicode__()} 
                for object in items]
        else:
            data = [{"value": str(object.pk)+"-"+object.__unicode__(), "label" : object.__unicode__()} 
                for object in items]
        return HttpResponse(json.dumps(data), content_type='application/json')

class AjaxSearch(View):
    def post(self, request):
        search = json.loads(request.POST["search"])
        searchdict = {}
        excludedict = {}
        textfilter = None
        statusfilter = None
        displayed_columns  = []
        searchvalues = ["id", "name", "inventorynumber", "devicetype__name", "room__name", "room__building__name"]
        for searchitem in search:
            key, value = searchitem.items()[0]

            if value[:4] == "not ":
                value = value[4:]
                dictionary = excludedict
            else:
                dictionary = searchdict

            if key == "manufacturer":
                value = value.split("-", 1)[0]
                if len(displayed_columns) < 8:
                    displayed_columns.append(("manufacturer", _("Manufacturer")))
                    searchvalues.append("manufacturer__name")
                if "manufacturer__in" in dictionary:
                    dictionary["manufacturer__in"].append(value)
                else:
                    dictionary["manufacturer__in"] = [value]

            elif key == "room":
                value = value.split("-", 1)[0]
                if "room__in" in dictionary:
                    dictionary["room__in"].append(value)
                else:
                    dictionary["room__in"] = [value]

            elif key == "devicetype":
                value = value.split("-", 1)[0]
                if "devicetype__in" in dictionary:
                    dictionary["devicetype__in"].append(value)
                else:
                    dictionary["devicetype__in"] = [value]

            elif key == "devicegroup":
                value = value.split("-", 1)[0]
                if len(displayed_columns) < 8:
                    displayed_columns.append(("group", _("Group")))
                    searchvalues.append("group__name")
                if "group__in" in dictionary:
                    dictionary["group__in"].append(value)
                else:
                    dictionary["group__in"] = [value]

            elif key == "user":
                value = value.split("-", 1)[0]
                if len(displayed_columns) < 8:
                    displayed_columns.append(("user", _("User")))
                    searchvalues.append("currentlending__owner__username")
                if value.lower() == "null":
                    dictionary["currentlending"] = None
                else:
                    dictionary["currentlending__owner__id"] = value

            elif key == "ipaddress":
                if len(displayed_columns) < 8:
                    displayed_columns.append(("ipaddress", _("IP-Address")))
                    searchvalues.append("ipaddress__address")
                if value.lower() == "null":
                    dictionary["ipaddress"] = None
                else:
                    dictionary["ipaddress__address__icontains"] = value

            elif key == "text":
                textfilter = value

            elif key == "status":
                statusfilter = value

            elif key == "id":
                try:
                    value = int(value)
                    context = {"device_list": Device.objects.filter(id=value).values("id", "name", "inventorynumber", "devicetype__name", "room__name", "room__building__name")}
                    return render_to_response('devices/searchresult.html', context, RequestContext(self.request))
                except:
                    return render_to_response('devices/searchempty.html', {}, RequestContext(self.request))
            elif key == "shortterm":
                if value.lower() == "yes":
                    dictionary["templending"] = True
                else:
                    dictionary["templending"] = False

        devices = Device.objects.filter(**searchdict)
        devices = devices.exclude(**excludedict)

        if statusfilter == "all":
                pass
        elif statusfilter == "available":
            devices = devices.filter(currentlending=None, archived=None, trashed=None)
        elif statusfilter == "unavailable":
            devices = devices.exclude(currentlending=None).filter(archived=None, trashed=None)
        elif statusfilter == "archived":
            devices = devices.exclude(archived=None)
        elif statusfilter == "trashed":
            devices = devices.exclude(trashed=None)
        else:
            devices = devices.filter(archived=None, trashed=None)

        if textfilter != None:
            if "text" in settings.SEARCHSTRIP:
                textfilter = textfilter.strip(settings.SEARCHSTRIP["text"]).strip()
            try:
                searchid = int(textfilter.replace(" ", ""))
                devices = devices.filter(Q(name__icontains=textfilter)|
                    Q(inventorynumber__icontains=textfilter.replace( " ", ""))|Q(serialnumber__icontains=textfilter.replace( " ", ""))|Q(id=searchid))
            except ValueError:
                devices = devices.filter(Q(name__icontains=textfilter)|
                    Q(inventorynumber__icontains=textfilter.replace( " ", ""))|Q(serialnumber__icontains=textfilter.replace( " ", "")))
        context = {
            "device_list": devices.values(*searchvalues),
            "columns": displayed_columns
        }
        return render_to_response('devices/searchresult.html', context, RequestContext(self.request))