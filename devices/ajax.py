# -*- coding: utf-8 -*-
import json
import urllib
import httplib
from httplib import ssl

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.template.loader import render_to_string
from django.views.generic.base import View
from django.http import HttpResponse
import pystache
from django.http import QueryDict
from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.dateparse import parse_date

from devices.models import Device, Room, Building, Manufacturer, Lending
from users.models import Lageruser, Department
from mail.models import MailTemplate
from devicetypes.models import Type
from devices.forms import AddForm
from devicegroups.models import Devicegroup
from devicetags.models import Devicetag
from Lagerregal.utils import UnicodeWriter
from csv import QUOTE_ALL


class AutocompleteDevice(View):
    def post(self, request):
        name = request.POST["name"]
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
    def post(self, request):
        name = request.POST["name"]
        devices = Lending.objects.filter(smalldevice__icontains=name).values("smalldevice").distinct()
        results = []
        for device in devices:
            device_json = {}
            device_json['label'] = device["smalldevice"]
            results.append(device_json)
        return HttpResponse(json.dumps(results), content_type='application/json')


class AutocompleteName(View):
    def post(self, request):
        name = request.POST["name"]
        classtype = request.POST["classtype"]
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
            retobjects = ["<li><a href='{0}'  class='alert-link'>{1}</a></li>".format(
                reverse(urlname, kwargs={"pk": obj[0]}), obj[1].decode('utf-8'))
                          for obj in objects.values_list("pk", "name")]
            return HttpResponse(json.dumps(retobjects), content_type='application/json')
        else:
            return HttpResponse("")


class AddDeviceField(View):
    def post(self, request):
        dform = QueryDict(query_string=unicode(request.POST["form"]).encode('utf-8'))
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
            print form.errors
            data["error"] = "Error: {0}".format(form.non_field_errors())
        return HttpResponse(json.dumps(data), content_type='application/json')


class LoadExtraform(View):
    def post(self, request):
        classname = request.POST["classname"]
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
    def post(self, request):
        template = request.POST["template"]
        device = {
            "currentlending": request.POST.get("device[currentlending]", ""),
            "description": request.POST.get("device[description]", ""),
            "devicetype": request.POST.get("device[devicetype]", ""),
            "group": request.POST.get("device[group]", ""),
            "hostname": request.POST.get("device[hostname]", ""),
            "inventorynumber": request.POST.get("device[inventorynumber]", ""),
            "manufacturer": request.POST.get("device[manufacturer]", ""),
            "name": request.POST.get("device[name]", ""),
            "room": request.POST.get("device[room]", ""),
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
        datadict = {"device": device, "user": {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name
        }}
        data = {"subject": pystache.render(template.subject, datadict),
                "body": pystache.render(template.body, datadict).replace("\n", "<br />")}
        return HttpResponse(json.dumps(data), content_type='application/json')


class LoadMailtemplate(View):

    def post(self, request):
        template = request.POST["template"]
        recipients = request.POST.get("recipients[]", [])
        if template == "":
            return HttpResponse("")
        template = get_object_or_404(MailTemplate, pk=template)
        data = {"subject": template.subject, "body": template.body}
        if isinstance(recipients, unicode):
            recipients = [recipients]
        newrecipients = [obj for obj in recipients]
        newrecipients += [obj.content_type.name[0].lower() + str(obj.object_id) for obj in
                          template.default_recipients.all()]
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
        elif facet == "tag":
            items = Devicetag.objects.filter(name__icontains=term)
        elif facet == "department":
            items = Department.objects.filter(name__icontains=term)
        else:
            return HttpResponse("")
        if invert:
            data = [
                {"value": "not " + str(object.pk) + "-" + object.__unicode__(), "label": "not " + object.__unicode__()}
                for object in items]
        else:
            data = [{"value": str(object.pk) + "-" + object.__unicode__(), "label": object.__unicode__()}
                    for object in items]
        return HttpResponse(json.dumps(data), content_type='application/json')


class UserLendings(View):
    def post(self, request):
        user = request.POST["user"]
        if user == "":
            return HttpResponse("")
        user = get_object_or_404(Lageruser, pk=user)
        data = {}
        data["devices"] = [[device["device__name"] if device["device__name"] else device["smalldevice"],
                            device["device__inventorynumber"], device["device__serialnumber"],
                            device["duedate"].strftime("%d.%m.%y") if device["duedate"] else "", device["pk"]]
                           for device in user.lending_set.filter(returndate=None).values("pk", "device__name",
                                                                                         "device__inventorynumber",
                                                                                         "device__serialnumber",
                                                                                         "smalldevice", "duedate")]

        return HttpResponse(json.dumps(data), content_type='application/json')


class AjaxSearch(View):
    def post(self, request):
        search = json.loads(request.POST["search"])
        searchdict = {}
        if request.user.departments.count() > 0:
            searchdict["department__in"] = list(request.user.departments.all())
        excludedict = {}
        search_q_list = []
        exclude_q_list = []
        textfilter = None
        statusfilter = None
        displayed_columns = []
        searchvalues = ["id", "name", "inventorynumber", "serialnumber", "devicetype__name", "room__name",
                        "room__building__name", "currentlending__owner__username", "currentlending__owner__id"]
        for searchitem in search:
            key, value = searchitem.items()[0]

            if value[:4] == "not ":
                value = value[4:]
                dictionary = excludedict
                q_list = exclude_q_list
            else:
                dictionary = searchdict
                q_list = search_q_list

            if key == "manufacturer":
                value = value.split("-", 1)[0]
                try:
                    value = int(value)
                except:
                    break
                if len(displayed_columns) < 8:
                    displayed_columns.append(("manufacturer", ugettext("Manufacturer")))
                    searchvalues.append("manufacturer__name")
                if "manufacturer__in" in dictionary:
                    dictionary["manufacturer__in"].append(value)
                else:
                    dictionary["manufacturer__in"] = [value]

            elif key == "room":
                value = value.split("-", 1)[0]
                try:
                    value = int(value)
                except:
                    break
                if "room__in" in dictionary:
                    dictionary["room__in"].append(value)
                else:
                    dictionary["room__in"] = [value]

            elif key == "devicetype":
                value = value.split("-", 1)[0]
                try:
                    value = int(value)
                except:
                    break
                if "devicetype__in" in dictionary:
                    dictionary["devicetype__in"].append(value)
                else:
                    dictionary["devicetype__in"] = [value]

            elif key == "devicegroup":
                value = value.split("-", 1)[0]
                try:
                    value = int(value)
                except:
                    break
                if len(displayed_columns) < 8:
                    displayed_columns.append(("group", ugettext("Group")))
                    searchvalues.append("group__name")
                if "group__in" in dictionary:
                    dictionary["group__in"].append(value)
                else:
                    dictionary["group__in"] = [value]

            elif key == "user":
                value = value.split("-", 1)[0]
                try:
                    value = int(value)
                    dictionary["currentlending__owner__id"] = value
                except:
                    if value.lower() == "null":
                        dictionary["currentlending"] = None
                    else:
                        q_list.append(Q(currentlending__owner__username__icontains=value) |
                                      Q(currentlending__owner__first_name__icontains=value) |
                                      Q(currentlending__owner__last_name__icontains=value))

            elif key == "ipaddress":
                if len(displayed_columns) < 8:
                    displayed_columns.append(("ipaddress", ugettext("IP-Address")))
                    searchvalues.append("ipaddress__address")
                if value.lower() == "null":
                    dictionary["ipaddress"] = None
                else:
                    dictionary["ipaddress__address__icontains"] = value

            elif key == "inventoried" or key == "trashed" or key == "archived":
                if value.startswith("before"):
                    value = value[7:]
                    modifier = "__lt"
                elif value.startswith("after"):
                    value = value[6:]
                    modifier = "__gt"
                else:
                    modifier = ""

                if len(displayed_columns) < 8:
                    displayed_columns.append((key, _("{0} on").format(key.capitalize())))
                    searchvalues.append(key)
                if key == "archived" or key == "inventoried":
                    statusfilter = "all"
                dictionary[key + modifier] = parse_date(value)

            elif key == "tag":
                value = value.split("-", 1)[0]
                try:
                    value = int(value)
                except:
                    break
                if "tags__in" in dictionary:
                    dictionary["tags__in"].append(value)
                else:
                    dictionary["tags__in"] = [value]

            elif key == "department":
                value = value.split("-", 1)[0]
                if value == "all":
                    del dictionary["department__in"]
                try:
                    value = int(value)
                except:
                    break
                if "department__in" in dictionary:
                    dictionary["department__in"].append(value)
                else:
                    dictionary["department__in"] = [value]

            elif key == "hostname":
                if len(displayed_columns) < 8:
                    displayed_columns.append(("hostname", ugettext("Hostname")))
                    searchvalues.append("hostname")

                dictionary["hostname__icontains"] = value

            elif key == "inventorynumber":
                dictionary["inventorynumber__icontains"] = value

            elif key == "serialnumber":
                dictionary["serialnumber__icontains"] = value

            elif key == "text":
                textfilter = value

            elif key == "status":
                statusfilter = value

            elif key == "id":
                try:
                    value = int(value)
                    context = {"device_list": Device.objects.filter(id=value).values("id", "name", "inventorynumber",
                                                                                     "devicetype__name", "room__name",
                                                                                     "room__building__name")}
                    return render(request, 'devices/searchresult.html', context)
                except Device.DoesNotExist:
                    return render(request, 'devices/searchempty.html')
            elif key == "shortterm":
                if value.lower() == "yes":
                    dictionary["templending"] = True
                else:
                    dictionary["templending"] = False

        devices = Device.objects.filter(*search_q_list, **searchdict)
        devices = devices.exclude(*exclude_q_list, **excludedict)

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
            SEARCHSTRIP = getattr(settings, "SEARCHSTRIP", [])
            if "text" in SEARCHSTRIP:
                textfilter = textfilter.strip(settings.SEARCHSTRIP["text"]).strip()
            try:
                searchid = int(textfilter.replace(" ", ""))
                devices = devices.filter(Q(name__icontains=textfilter) |
                                         Q(inventorynumber__icontains=textfilter.replace(" ", "")) | Q(
                    serialnumber__icontains=textfilter.replace(" ", "")) | Q(id=searchid))
            except ValueError:
                devices = devices.filter(Q(name__icontains=textfilter) |
                                         Q(inventorynumber__icontains=textfilter.replace(" ", "")) | Q(
                    serialnumber__icontains=textfilter.replace(" ", "")))
        if "format" in request.POST:
            if request.POST["format"] == "csv":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="searchresult.csv"'

                writer = UnicodeWriter(response, delimiter=",", quotechar='"', quoting=QUOTE_ALL)
                headers = [ugettext("ID"), ugettext("Device"), ugettext("Inventorynumber"), ugettext("Serialnumber"),
                           ugettext("Devicetype"), ugettext("Room"), ugettext("Building")]
                if len(displayed_columns) > 0:
                    headers.extend([col[1] for col in displayed_columns])
                writer.writerow(headers)
                for device in devices.values_list(*searchvalues):
                    writer.writerow(device)

                return response
        context = {
            "device_list": devices.values(*searchvalues),
            "columns": displayed_columns
        }
        return render(request, 'devices/searchresult.html', context)


class PuppetDetails(View):

    def post(self, request):
        searchvalue = request.POST["id"]
        params = urllib.urlencode({'query': '["in", "certname",["extract", "certname",' +
                                            '["select_facts",["and",["=", "name","' +
                                            settings.PUPPETDB_SETTINGS['query_fact'] + '"],' +
                                            '["=","value","' + searchvalue + '"]]]]]'})
        context = ssl.create_default_context(cafile=settings.PUPPETDB_SETTINGS['cacert'])
        context.load_cert_chain(certfile=settings.PUPPETDB_SETTINGS['cert'],
                                keyfile=settings.PUPPETDB_SETTINGS['key'])
        conn = httplib.HTTPSConnection(settings.PUPPETDB_SETTINGS['host'],
                                       settings.PUPPETDB_SETTINGS['port'],
                                       context=context)
        conn.request("GET", settings.PUPPETDB_SETTINGS['req'] + params)
        res = conn.getresponse()
        if res.status != httplib.OK:
            return HttpResponse('Failed to fetch puppet details from ' +
                                settings.PUPPETDB_SETTINGS['host'])
        context = {
            'puppetdetails': json.loads(res.read())
        }
        return render(request, 'devices/puppetdetails.html', context)

class PuppetSoftware(View):

    def post(self, request):
        searchvalue = request.POST["id"]
        software_fact = settings.PUPPETDB_SETTINGS['software_fact']
        query_fact = settings.PUPPETDB_SETTINGS['query_fact']

        params = urllib.urlencode({'query': '["and", [ "=", "name", "' + software_fact + '"],' +
                                            '["in", "certname",["extract", "certname",' +
                                            '["select_facts",["and",["=", "name","' + query_fact + '"],' +
                                            '["=","value","' + searchvalue + '"]]]]]]'})
        context = ssl.create_default_context(cafile=settings.PUPPETDB_SETTINGS['cacert'])
        context.load_cert_chain(certfile=settings.PUPPETDB_SETTINGS['cert'],
                                keyfile=settings.PUPPETDB_SETTINGS['key'])
        conn = httplib.HTTPSConnection(settings.PUPPETDB_SETTINGS['host'],
                                       settings.PUPPETDB_SETTINGS['port'],
                                       context=context)
        req = settings.PUPPETDB_SETTINGS['req'] + params
        conn.request("GET", settings.PUPPETDB_SETTINGS['req'] + params)
        res = conn.getresponse()
        if res.status != httplib.OK:
            return HttpResponse('Failed to fetch puppet details from ' +
                                settings.PUPPETDB_SETTINGS['host'])

        try:
            res = json.loads(res.read())[0]
            software = res['value']
            context = {
                'puppetsoftware': software.values()
            }
        except:
            return HttpResponse('Malformed puppet software fact.')

        return render(request, 'devices/puppetsoftware.html', context)
