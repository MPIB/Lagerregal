import http.client
import json
import urllib
from http.client import ssl

from django.conf import settings
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic.base import View

import pystache

from devicegroups.models import Devicegroup
from devices.forms import AddForm
from devices.models import Building
from devices.models import Device
from devices.models import Lending
from devices.models import Manufacturer
from devices.models import Room
from devicetypes.models import Type
from mail.models import MailTemplate
from users.models import Lageruser


class AutocompleteDevice(View):
    def get(self, request):
        name = request.GET["name"]
        devices = Device.objects.filter(name__icontains=name).values("name").distinct()[:20]
        results = []
        for device in devices:
            device_json = {}
            device_json['id'] = device["name"]
            device_json['label'] = device["name"]
            device_json['value'] = device["name"]
            results.append(device_json)
        return HttpResponse(json.dumps(results), content_type='application/json')


class AutocompleteSmallDevice(View):
    def get(self, request):
        name = request.GET["name"]
        devices = Lending.objects.filter(smalldevice__icontains=name).values("smalldevice").distinct()
        results = []
        for device in devices:
            device_json = {}
            device_json['label'] = device["smalldevice"]
            results.append(device_json)
        return HttpResponse(json.dumps(results), content_type='application/json')


class AutocompleteName(View):
    def get(self, request):
        name = request.GET["name"]
        classtype = request.GET["classtype"]
        if classtype == "type":
            objects = Type.objects.filter(name__icontains=name)[:20]
            urlname = "type-detail"
        elif classtype == "room":
            objects = Room.objects.filter(name__icontains=name)[:20]
            urlname = "room-detail"
        elif classtype == "building":
            objects = Building.objects.filter(name__icontains=name)[:20]
            urlname = "building-detail"
        elif classtype == "manufacturer":
            objects = Manufacturer.objects.filter(name__icontains=name)[:20]
            urlname = "manufacturer-detail"
        elif classtype == "manufacturer":
            objects = Manufacturer.objects.filter(name__icontains=name)[:20]
            urlname = "manufacturer-detail"
        else:
            return HttpResponse("")
        if len(objects) > 0:
            retobjects = [
                "<li><a href='{0}'  class='alert-link'>{1}</a></li>".format(
                    reverse(urlname, kwargs={"pk": obj[0]}), obj[1]
                ) for obj in objects.values_list("pk", "name")
            ]
            return HttpResponse(json.dumps(retobjects), content_type='application/json')
        else:
            return HttpResponse("")


class AddDeviceField(View):
    def post(self, request):
        dform = QueryDict(query_string=str(request.POST["form"]).encode('utf-8'))
        classname = dform["classname"]
        if classname == "manufacturer":
            form = modelform_factory(Manufacturer, exclude=(), form=AddForm)(dform)
        elif classname == "devicetype":
            form = modelform_factory(Type, exclude=(), form=AddForm)(dform)
        elif classname == "room":
            form = modelform_factory(Room, exclude=(), form=AddForm)(dform)
        elif classname == "group":
            form = modelform_factory(Devicegroup, exclude=(), form=AddForm)(dform)
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
                    newitem.building = form.cleaned_data["building"]
                    newitem.section = form.cleaned_data["section"]
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
    def get(self, request):
        classname = request.GET["classname"]
        if classname == "manufacturer":
            form = modelform_factory(Manufacturer, exclude=(), form=AddForm)()
        elif classname == "devicetype":
            form = modelform_factory(Type, exclude=(), form=AddForm)()
        elif classname == "room":
            form = modelform_factory(Room, exclude=(), form=AddForm)()
        elif classname == "group":
            form = modelform_factory(Devicegroup, exclude=(), form=AddForm)()
        else:
            return HttpResponse("")

        return HttpResponse(render_to_string('snippets/formfields.html', {"form": form}))


class PreviewMail(View):
    def get(self, request):
        template = request.GET["template"]
        device = {
            "currentlending": request.GET.get("device[currentlending]", ""),
            "description": request.GET.get("device[description]", ""),
            "devicetype": request.GET.get("device[devicetype]", ""),
            "group": request.GET.get("device[group]", ""),
            "hostname": request.GET.get("device[hostname]", ""),
            "inventorynumber": request.GET.get("device[inventorynumber]", ""),
            "manufacturer": request.GET.get("device[manufacturer]", ""),
            "name": request.GET.get("device[name]", ""),
            "room": request.GET.get("device[room]", ""),
            "serialnumber": request.GET.get("device[serialnumber]", ""),
            "templending": request.GET.get("device[templending]", ""),
            "webinterface": request.GET.get("device[webinterface]", "")
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
        datadict = {"device": device, "user": {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name
        }}
        data = {"subject": pystache.render(template.subject, datadict),
                "body": pystache.render(template.body, datadict).replace("\n", "<br />")}
        return HttpResponse(json.dumps(data), content_type='application/json')


class LoadMailtemplate(View):

    def get(self, request):
        template = request.GET["template"]
        recipients = request.GET.get("recipients[]", [])
        if template == "":
            return HttpResponse("")
        template = get_object_or_404(MailTemplate, pk=template)
        data = {"subject": template.subject, "body": template.body}
        if isinstance(recipients, str):
            recipients = [recipients]
        newrecipients = [obj for obj in recipients]
        newrecipients += [obj.content_type.name[0].lower() + str(obj.object_id) for obj in
                          template.default_recipients.all()]
        newrecipients = list(set(newrecipients))
        data["recipients"] = newrecipients
        return HttpResponse(json.dumps(data), content_type='application/json')


class UserLendings(View):
    def get(self, request):
        user = request.GET["user"]
        if user == "":
            return HttpResponse("")
        user = get_object_or_404(Lageruser, pk=user)
        data = {}
        data["devices"] = [
            [
                device["device__name"] if device["device__name"] else device["smalldevice"],
                device["device__inventorynumber"],
                device["device__serialnumber"],
                device["duedate"].strftime("%d.%m.%y") if device["duedate"] else "",
                device["pk"],
            ]
            for device in user.lending_set.filter(returndate=None).values(
                "pk", "device__name", "device__inventorynumber",
                "device__serialnumber", "smalldevice", "duedate",
            )
        ]

        return HttpResponse(json.dumps(data), content_type='application/json')


class PuppetDetails(View):

    def get(self, request, device):
        query = (
            '["in", "certname", ["extract", "certname", ["select_facts", '
            '["and", ["=", "name", "{}"], ["=", "value", "{}"]]]]]'
        ).format(settings.PUPPETDB_SETTINGS['query_fact'], str(device))
        params = urllib.parse.urlencode({'query': query})

        context = ssl.create_default_context(cafile=settings.PUPPETDB_SETTINGS['cacert'])
        context.load_cert_chain(
            certfile=settings.PUPPETDB_SETTINGS['cert'],
            keyfile=settings.PUPPETDB_SETTINGS['key'],
        )
        conn = http.client.HTTPSConnection(
            settings.PUPPETDB_SETTINGS['host'],
            settings.PUPPETDB_SETTINGS['port'],
            context=context,
        )
        conn.request("GET", settings.PUPPETDB_SETTINGS['req'] + params)
        res = conn.getresponse()
        if res.status != http.client.OK:
            return HttpResponse('Failed to fetch puppet details from '
                                + settings.PUPPETDB_SETTINGS['host'])
        context = {
            'puppetdetails': json.loads(res.read().decode())
        }
        return render(request, 'devices/puppetdetails.html', context)


class PuppetSoftware(View):

    def get(self, request, device):
        software_fact = settings.PUPPETDB_SETTINGS['software_fact']
        query_fact = settings.PUPPETDB_SETTINGS['query_fact']

        query = (
            '["and", ["=", "name", "{}"], ["in", "certname", '
            '["extract", "certname", ["select_facts", ["and", '
            '["=", "name", "{}"], ["=", "value", "{}"]]]]]]'
        ).format(software_fact, query_fact, str(device))
        params = urllib.parse.urlencode({'query': query})

        context = ssl.create_default_context(cafile=settings.PUPPETDB_SETTINGS['cacert'])
        context.load_cert_chain(
            certfile=settings.PUPPETDB_SETTINGS['cert'],
            keyfile=settings.PUPPETDB_SETTINGS['key'],
        )
        conn = http.client.HTTPSConnection(
            settings.PUPPETDB_SETTINGS['host'],
            settings.PUPPETDB_SETTINGS['port'],
            context=context,
        )
        conn.request("GET", settings.PUPPETDB_SETTINGS['req'] + params)
        res = conn.getresponse()
        if res.status != http.client.OK:
            return HttpResponse('Failed to fetch puppet details from '
                                + settings.PUPPETDB_SETTINGS['host'])

        try:
            res = json.loads(res.read().decode())[0]
            software = res['value']
            context = {
                'puppetsoftware': list(software.values())
            }
        except:
            return HttpResponse('Malformed puppet software fact.')

        return render(request, 'devices/puppetsoftware.html', context)
