# coding: utf-8
from __future__ import unicode_literals

import datetime
import time
import csv

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView, SingleObjectMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import Group
from django.shortcuts import render
from reversion.models import Version
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.contrib import messages
from django.utils.timezone import utc
from django.utils import timezone
from reversion import revisions as reversion
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import atomic
from django.conf import settings
from django.db.models.query import QuerySet
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import SuspiciousOperation
from django.http import Http404

from devices.models import Device, Template, Room, Building, Manufacturer, Lending, Note, Bookmark, Picture
from devicetypes.models import TypeAttribute, TypeAttributeValue
from network.models import IpAddress
from mail.models import MailTemplate, MailHistory
from devices.forms import IpAddressForm, LendForm, DeviceViewForm, IpAddressPurposeForm
from devices.forms import ViewForm, DeviceForm, DeviceMailForm, VIEWSORTING, VIEWSORTING_DEVICES, FilterForm, \
    DeviceStorageForm, ReturnForm, DeviceGroupFilterForm
from devicetags.forms import DeviceTagForm
from users.models import Lageruser, Department
from Lagerregal.utils import PaginationMixin
from devicetags.models import Devicetag
from permission.decorators import permission_required
from django.db.models import Q


@permission_required('devices.read_device', raise_exception=True)
class DeviceList(PaginationMixin, ListView):
    context_object_name = 'device_list'
    template_name = 'devices/device_list.html'
    viewfilter = None
    viewsorting = None

    def post(self, request):
        '''post-requesting the detail-view of device by id'''
        if 'deviceid' in request.POST:
            return HttpResponseRedirect(reverse('device-detail', kwargs={'pk': request.POST['deviceid']}))
        else:
            return HttpResponseRedirect(reverse('device-list'))

    def get_queryset(self):
        '''method for query results and display it depending on existing filters (viewfilter, department)'''
        self.viewfilter = self.kwargs.get("filter", "active")
        devices = None
        lendings = None

        # filtering devices by status
        # possible status: all, active, lent, archived, trash, overdue,
        # return soon, short term, bookmarked
        if self.viewfilter == "all":
            devices = Device.objects.all()
        elif self.viewfilter == "available":
            devices = Device.active().filter(currentlending=None)
        elif self.viewfilter == "lent":
            lendings = Lending.objects.filter(returndate=None)
        elif self.viewfilter == "archived":
            devices = Device.objects.exclude(archived=None)
        elif self.viewfilter == "trashed":
            devices = Device.objects.exclude(trashed=None)
        elif self.viewfilter == "overdue":
            lendings = Lending.objects.filter(returndate=None, duedate__lt=datetime.date.today())
        elif self.viewfilter == "returnsoon":
            soon = datetime.date.today() + datetime.timedelta(days=10)
            lendings = Lending.objects.filter(returndate=None, duedate__lte=soon,
                                              duedate__gt=datetime.date.today())
        elif self.viewfilter == "temporary":
            devices = Device.active().filter(templending=True)
        elif self.viewfilter == "bookmark":
            if self.request.user.is_authenticated:
                devices = self.request.user.bookmarks.all()
        else:
            devices = Device.active()

        self.departmentfilter = self.kwargs.get("department", "all")
        # if user has departments: set departments as filter
        if hasattr(self.request.user, 'departments'):
            if self.request.user.departments.count() > 0:
                self.departmentfilter = self.kwargs.get("department", "my")

        if self.departmentfilter != "all" and self.departmentfilter != "my":
            try:
                departmentid = int(self.departmentfilter)
                self.departmentfilter = Department.objects.get(id=departmentid)
            except:
                self.departmentfilter = Department.objects.get(name=self.departmentfilter)

        if self.departmentfilter == "my":
            self.departmentfilter = self.request.user.departments.all()

        # filtering lent or overdue devices
        if self.viewfilter == "lent" or self.viewfilter == "overdue" or self.viewfilter == "returnsoon":
            if isinstance(self.departmentfilter, (list, tuple, QuerySet)):
                lendings = lendings.filter(owner__departments__in=self.departmentfilter)
                self.departmentfilter = "my"
            elif self.departmentfilter != "all":
                lendings = lendings.filter(owner__departments=self.departmentfilter)
                self.departmentfilter = self.departmentfilter.id
            lendings = lendings.exclude(~Q(device__department__in=self.request.user.departments.all()) &
                                        ~Q(device=None), device__is_private=True)
            return lendings.values("device__id", "device__name", "device__inventorynumber",
                                   "device__devicetype__name", "device__room__name", "device__group",
                                   "device__room__building__name", "owner__username", "owner__id",
                                   "duedate", "smalldevice")
        else:
            if isinstance(self.departmentfilter, (list, tuple, QuerySet)):
                devices = devices.filter(department__in=self.departmentfilter)
                self.departmentfilter = "my"
            elif self.departmentfilter != "all":
                devices = devices.filter(department=self.departmentfilter)
                self.departmentfilter = self.departmentfilter.id
            if hasattr(self.request.user, 'departments'):
                devices = devices.exclude(~Q(department__in=self.request.user.departments.all()), is_private=True)
            self.viewsorting = self.kwargs.get("sorting", "name")
            if self.viewsorting in [s[0] for s in VIEWSORTING_DEVICES]:
                devices = devices.order_by(self.viewsorting)

            return devices.values("id", "name", "inventorynumber", "devicetype__name", "room__name",
                                  "room__building__name",
                                  "group__name", "currentlending__owner__username", "currentlending__duedate")

    def get_context_data(self, **kwargs):
        '''method for getting context data (filter, time, templates, breadcrumbs)'''
        context = super(DeviceList, self).get_context_data(**kwargs)

        # getting filters
        context["viewform"] = DeviceViewForm(initial={
            'viewfilter': self.viewfilter,
            "viewsorting": self.viewsorting,
            "departmentfilter": self.departmentfilter
        })

        context["today"] = datetime.datetime.today()
        context["template_list"] = Template.objects.all()
        context["viewfilter"] = self.viewfilter
        context["breadcrumbs"] = [[reverse("device-list"), _("Devices")]]

        # add page number to breadcrumbs
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


@permission_required('devices.read_device', raise_exception=True)
class ExportCsv(View):
    def post(self, request):

        if "format" in request.POST:
            if request.POST["format"] == "csv":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="' + str(int(time.time())) + '_searchresult.csv"'
                devices = None
                searchvalues = ["id", "name", "inventorynumber", "devicetype__name", "room__name", "group__name"]

                if request.POST['viewfilter'] == "active":
                    devices = Device.active()
                elif request.POST['viewfilter'] == "all":
                    devices = Device.objects.all()
                elif request.POST['viewfilter'] == "available":
                    devices = Device.active().filter(currentlending=None)
                elif request.POST['viewfilter'] == "lent":
                    devices = Lending.objects.filter(returndate=None)
                elif request.POST['viewfilter'] == "archived":
                    devices = Device.objects.exclude(archived=None)
                elif request.POST['viewfilter'] == "trashed":
                    devices = Device.objects.exclude(trashed=None)
                elif request.POST['viewfilter'] == "overdue":
                    devices = Lending.objects.filter(returndate=None, duedate__lt=datetime.date.today())
                elif request.POST['viewfilter'] == "returnsoon":
                    soon = datetime.date.today() + datetime.timedelta(days=10)
                    devices = Lending.objects.filter(returndate=None, duedate__lte=soon,
                                                          duedate__gt=datetime.date.today())
                elif request.POST['viewfilter'] == "temporary":
                    devices = Device.active().filter(templending=True)
                elif request.POST['viewfilter'] == "bookmark":
                    if self.request.user.is_authenticated:
                        devices = self.request.user.bookmarks.all()

                if request.POST["departmentfilter"] == "my":
                    devices = devices.filter(department__in=request.user.departments.all())  # does this work?
                elif request.POST["departmentfilter"].isdigit():
                    devices = devices.filter(department__in=Department.objects.filter(id=int(request.POST["departmentfilter"])))
                elif request.POST["departmentfilter"] == "all":
                    pass

                writer = csv.writer(response, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
                headers = [_("ID"), _("Device"), _("Inventorynumber"),
                                    _("Devicetype"), _("Room"), _("Devicegroup")]
                writer.writerow(headers)
                for device in devices.values_list(*searchvalues):
                    writer.writerow(device)
                return response


@permission_required('devices.read_device', raise_exception=True)
class DeviceDetail(DetailView):
    # get related data to chosen device
    queryset = Device.objects \
        .select_related("manufacturer", "devicetype", "currentlending", "currentlending__owner", "department",
                        "room", "room__building") \
        .prefetch_related("pictures", )
    context_object_name = 'device'
    object = None

    def get_object(self, queryset=None):
        if self.object is not None:
            return self.object

        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.queryset.filter(pk=pk)
        self.object = get_object_or_404(queryset)
        return self.object

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceDetail, self).get_context_data(**kwargs)
        context['usedset'] = Device.objects.filter(used_in=self.object)

        # Add in a QuerySet of all the books

        # ip context data
        context['ipaddressform'] = IpAddressForm()
        context["ipaddressform"].fields["ipaddresses"].queryset = IpAddress.objects.filter(
            department=self.object.department, device=None, user=None)

        # tag context data
        context['tagform'] = DeviceTagForm()
        context['tagform'].fields["tags"].queryset = Devicetag.objects.exclude(devices=context["device"])

        # lending history, eidt history, mail history
        context["lending_list"] = Lending.objects.filter(device=context["device"])\
                                      .select_related("owner").order_by("-pk")[:10]
        context["version_list"] = Version.objects.filter(object_id=context["device"].id,
                                                         content_type_id=ContentType.objects.get(
                                                             model='device').id) \
                                      .select_related("revision", "revision__user").order_by("-pk")[:10]
        context["mail_list"] = MailHistory.objects.filter(device=context["device"])\
                                   .select_related("sent_by").order_by("-pk")[:10]

        context["today"] = datetime.datetime.utcnow().replace(tzinfo=utc)
        context["weekago"] = context["today"] - datetime.timedelta(days=7)
        context["attributevalue_list"] = TypeAttributeValue.objects.filter(device=context["device"])
        context["lendform"] = LendForm()
        mailinitial = {}

        # get user infos if device is lend
        if context["device"].currentlending is not None:
            currentowner = context["device"].currentlending.owner
            mailinitial["owner"] = currentowner
            mailinitial["emailrecipients"] = ("u" + str(currentowner.id), currentowner.username)
        try:
            mailinitial["mailtemplate"] = MailTemplate.objects.get(usage="reminder")
            mailinitial["emailsubject"] = mailinitial["mailtemplate"].subject
            mailinitial["emailbody"] = mailinitial["mailtemplate"].body
        except:
            messages.error(self.request, _('Please create reminder mail template'))
        # mail context data
        context["mailform"] = DeviceMailForm(initial=mailinitial)
        context["mailform"].fields["mailtemplate"].queryset = MailTemplate.objects.all()
        versions = Version.objects.get_for_object(context["device"])

        if len(versions) != 0:
            context["lastedit"] = versions[0]

        if self.object.department:
            dep = self.object.department.name
        else:
            dep = "all"

        if dep in settings.LABEL_TEMPLATES:
            if "device" in settings.LABEL_TEMPLATES[dep]:
                context["display_printbutton"] = True
                context["label_path"] = settings.LABEL_TEMPLATES[dep]["device"][0]
                context["label_js"] = ""
                for attribute in settings.LABEL_TEMPLATES[dep]["device"][1]:
                    if attribute == "id":
                        context["label_js"] += "\nlabel.setObjectText('{0}', '{1:07d}');".format(attribute,
                                                                                                 getattr(
                                                                                                     context["device"],
                                                                                                     attribute))
                    else:
                        context["label_js"] += "\nlabel.setObjectText('{0}', '{1}');".format(attribute,
                                                                                             getattr(context["device"],
                                                                                                     attribute))

        # add data to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name)]

        return context


# to do
@permission_required('devices.change_device', raise_exception=True)
class DeviceIpAddressRemove(View):
    template_name = 'devices/unassign_ipaddress.html'

    def get(self, request, *args, **kwargs):
        context = {"device": get_object_or_404(Device, pk=kwargs["pk"]),
                   "ipaddress": get_object_or_404(IpAddress, pk=kwargs["ipaddress"])}
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name),
            ("", _("Unassign IP-Addresses"))]

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        device = get_object_or_404(Device, pk=kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        ipaddress.device = None
        ipaddress.purpose = None
        reversion.set_comment(_("Removed from Device {0}".format(device.name)))
        ipaddress.save()

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


@permission_required('devices.change_device', raise_exception=True)
class DeviceIpAddress(FormView):
    template_name = 'devices/assign_ipaddress.html'
    form_class = IpAddressForm
    success_url = "/devices"

    def get_context_data(self, **kwargs):
        context = super(DeviceIpAddress, self).get_context_data(**kwargs)
        device = context["form"].cleaned_data["device"]
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": device.pk}), device.name),
            ("", _("Assign IP-Addresses"))]

        return context

    def form_valid(self, form):
        ipaddresses = form.cleaned_data["ipaddresses"]
        device = form.cleaned_data["device"]

        if device.archived is not None:
            messages.error(self.request, _("Archived Devices can't get new IP-Addresses"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))

        reversion.set_comment(_("Assigned to Device {0}".format(device.name)))
        for ipaddress in ipaddresses:
            ipaddress.device = device
            ipaddress.save()

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


@permission_required('devices.change_device', raise_exception=True)
class DeviceIpAddressPurpose(FormView):
    template_name = 'devices/assign_ipaddress.html'
    form_class = IpAddressPurposeForm
    success_url = "/devices"

    def get_context_data(self, **kwargs):
        context = super(DeviceIpAddressPurpose, self).get_context_data(**kwargs)
        device = get_object_or_404(Device, pk=self.kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=self.kwargs["ipaddress"])
        if ipaddress.purpose:
            context["form"].fields["purpose"].initial = ipaddress.purpose
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": device.pk}), device.name),
            ("", _("Set Purpose for {0}").format(ipaddress.address))]
        return context

    def form_valid(self, form):
        purpose = form.cleaned_data["purpose"]
        device = get_object_or_404(Device, pk=self.kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=self.kwargs["ipaddress"])
        reversion.set_comment(_("Assigned to Device {0}".format(device.name)))
        ipaddress.purpose = purpose
        ipaddress.save()

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


@permission_required('devices.read_device', raise_exception=True)
class DeviceLendingList(PaginationMixin, ListView):
    context_object_name = 'lending_list'
    template_name = 'devices/device_lending_list.html'

    def get_queryset(self):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        return Lending.objects.filter(device=device).order_by("-pk")

    def get_context_data(self, **kwargs):
        context = super(DeviceLendingList, self).get_context_data(**kwargs)
        context["device"] = get_object_or_404(Device, pk=self.kwargs["pk"])
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name),
            ("", _("Lending"))]
        return context


@permission_required('devices.add_device', raise_exception=True)
class DeviceCreate(CreateView):
    model = Device
    template_name = 'devices/device_form.html'
    form_class = DeviceForm

    def get_initial(self):
        initial = super(DeviceCreate, self).get_initial()
        creator = self.request.user.pk
        templateid = self.kwargs.pop("templateid", None)
        if templateid is not None:
            initial += get_object_or_404(Template, pk=templateid).get_as_dict()
        copyid = self.kwargs.pop("copyid", None)
        if copyid is not None:
            for key, value in get_object_or_404(Device, pk=copyid).get_as_dict().items():
                initial[key] = value
            initial["deviceid"] = copyid
        initial["creator"] = creator

        if self.request.user.main_department:
            initial["department"] = self.request.user.main_department

        try:
            initial["emailtemplate"] = MailTemplate.objects.get(usage="new")
            initial["emailrecipients"] = [obj.content_type.name[0].lower() + str(obj.object_id) for obj in
                                          initial["emailtemplate"].default_recipients.all()]
            initial["emailsubject"] = initial["emailtemplate"].subject
            initial["emailbody"] = initial["emailtemplate"].body
        except Exception as e:
            if not settings.TEST_MODE:
                print(e)
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceCreate, self).get_context_data(**kwargs)
        context["form"].fields["department"].queryset = self.request.user.departments.all()
        context["form"].fields["emailtemplate"].queryset = MailTemplate.objects.all()
        context['actionstring'] = "Create new Device"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            ("", _("Create new device"))]
        return context

    def form_valid(self, form):
        if form.cleaned_data["department"]:
            if not form.cleaned_data["department"] in self.request.user.departments.all():
                return HttpResponseBadRequest()
        form.cleaned_data["creator"] = self.request.user
        reversion.set_comment(_("Created"))
        r = super(DeviceCreate, self).form_valid(form)
        for key, value in form.cleaned_data.items():
            if key.startswith("attribute_") and value != "":
                attributenumber = key.split("_")[1]
                typeattribute = get_object_or_404(TypeAttribute, pk=attributenumber)
                attribute = TypeAttributeValue()
                attribute.device = self.object
                attribute.typeattribute = typeattribute
                attribute.value = value
                attribute.save()
        if form.cleaned_data["emailrecipients"] and form.cleaned_data["emailtemplate"]:
            recipients = []
            for recipient in form.cleaned_data["emailrecipients"]:
                if recipient[0] == "g":
                    group = get_object_or_404(Group, pk=recipient[1:])
                    recipients += group.user_set.all().values_list("email")[0]
                else:
                    recipients.append(get_object_or_404(Lageruser, pk=recipient[1:]).email)
            recipients = list(set(recipients))
            template = form.cleaned_data["emailtemplate"]
            if form.cleaned_data["emailedit"]:
                template.subject = form.cleaned_data["emailsubject"]
                template.body = form.cleaned_data["emailbody"]
            template.send(request=self.request, recipients=recipients,
                          data={"device": self.object, "user": self.request.user})
            messages.success(self.request, _('Mail successfully sent'))

        if "uses" in form.changed_data:
            for element in form.cleaned_data["uses"]:
                used_device = Device.objects.filter(id=element)[0]
                used_device.used_in = self.object
                used_device.save()

        messages.success(self.request, _('Device was successfully created.'))
        return r


@permission_required('devices.change_device', raise_exception=True)
class DeviceUpdate(UpdateView):
    model = Device
    template_name = 'devices/device_form.html'
    form_class = DeviceForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceUpdate, self).get_context_data(**kwargs)
        context["form"].fields["department"].queryset = self.request.user.departments.all()
        context['actionstring'] = _("Update")
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name),
            ("", _("Edit"))]
        context["template_list"] = MailTemplate.objects.all()
        context["form"].fields["emailtemplate"].queryset = MailTemplate.objects.all()
        return context

    def form_valid(self, form):
        if form.cleaned_data["department"]:
            if not form.cleaned_data["department"] in self.request.user.departments.all():
                return HttpResponseBadRequest()
        device = self.object
        if device.archived is not None:
            messages.error(self.request, _("Archived Devices can't be edited"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))

        if form.cleaned_data["comment"] == "":
            reversion.set_comment(_("Updated"))
        else:
            reversion.set_comment(form.cleaned_data["comment"])

        if device.devicetype is not None:
            if form.cleaned_data["devicetype"] is None or device.devicetype.pk != form.cleaned_data["devicetype"].pk:
                TypeAttributeValue.objects.filter(device=device.pk).delete()
        for key, value in form.cleaned_data.items():
            if key.startswith("attribute_") and value != "":
                attributenumber = key.split("_")[1]
                typeattribute = get_object_or_404(TypeAttribute, pk=attributenumber)
                try:
                    attribute = TypeAttributeValue.objects.filter(device=device.pk).get(typeattribute=attributenumber)
                except:
                    attribute = TypeAttributeValue()
                    attribute.device = device
                    attribute.typeattribute = typeattribute
                attribute.value = value
                attribute.save()
            elif key.startswith("attribute_") and value == "":
                attributenumber = key.split("_")[1]
                try:
                    TypeAttributeValue.objects.filter(device=device.pk).get(typeattribute=attributenumber).delete()
                except:
                    pass

        if form.cleaned_data["emailrecipients"] and form.cleaned_data["emailtemplate"]:
            recipients = []
            for recipient in form.cleaned_data["emailrecipients"]:
                if recipient[0] == "g":
                    group = get_object_or_404(Group, pk=recipient[1:])
                    recipients += group.user_set.all().values_list("email")[0]
                else:
                    recipients.append(get_object_or_404(Lageruser, pk=recipient[1:]).email)
            recipients = list(set(recipients))
            template = form.cleaned_data["emailtemplate"]
            if form.cleaned_data["emailedit"]:
                template.subject = form.cleaned_data["emailsubject"]
                template.body = form.cleaned_data["emailbody"]
            template.send(request=self.request, recipients=recipients,
                          data={"device": device, "user": self.request.user})
            messages.success(self.request, _('Mail successfully sent'))

        if "uses" in form.changed_data:
            for element in form.initial["uses"]:
                # if element was removed
                if element not in form.cleaned_data["uses"]:
                    used_device = Device.objects.filter(id=int(element))[0]
                    used_device.used_in = None
                    used_device.save()
            for element in form.cleaned_data["uses"]:
                # if element was added
                if element not in form.initial["uses"]:
                    used_device = Device.objects.filter(id=int(element))[0]
                    used_device.used_in = self.object
                    used_device.save()

        messages.success(self.request, _('Device was successfully updated.'))
        return super(DeviceUpdate, self).form_valid(form)


@permission_required('devices.delete_device', raise_exception=True)
class DeviceDelete(DeleteView):
    model = Device
    success_url = reverse_lazy('device-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context


@permission_required('devices.lend_device', raise_exception=True)
class DeviceLend(FormView):
    template_name = 'devices/device_lend.html'
    form_class = LendForm

    def get_context_data(self, **kwargs):
        context = super(DeviceLend, self).get_context_data(**kwargs)
        context['actionstring'] = "Mark device as lend"
        context['form_scripts'] = "$('#id_owner').select2();"
        if "device" in self.request.POST:
            deviceid = self.request.POST["device"]
            if deviceid != "":
                device = get_object_or_404(Device, pk=deviceid)
                context["breadcrumbs"] = [
                    (reverse("device-list"), _("Devices")),
                    ("", _("Lend"))]
                return context
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            ("", _("Lend"))]
        if self.kwargs and 'pk' in self.kwargs:
            device = get_object_or_404(Device, pk=self.kwargs['pk'])
            context["breadcrumbs"] = context["breadcrumbs"][:-1] + [(reverse("device-detail", kwargs={"pk": device.pk}), device.name)] + context['breadcrumbs'][-1:]
        return context

    def get_form_kwargs(self):
        kwargs = super(DeviceLend, self).get_form_kwargs()
        kwargs.update(self.kwargs)
        return kwargs

    def form_valid(self, form):
        device = None
        templates = []
        if form.cleaned_data["device"] and form.cleaned_data["device"] != "":
            device = form.cleaned_data["device"]
            if device.archived is not None:
                messages.error(self.request, _("Archived Devices can't be lent"))
                return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))
            if device.currentlending is not None:
                lending = device.currentlending
                lending.returndate = datetime.date.today()
                lending.save()
                lending = Lending()
            else:
                lending = Lending()
            try:
                templates.append(MailTemplate.objects.get(usage="lent"))
            except:
                messages.error(self.request, _('MAIL NOT SENT - Template for lent devices does not exist for your main department'))

            if form.cleaned_data["room"]:
                device.room = form.cleaned_data["room"]
                try:
                    templates.append(MailTemplate.objects.get(usage="room"))
                except:
                    messages.error(self.request, _('MAIL NOT SENT - Template for room change does not exist for your main department'))
            if templates:
                for template in templates:
                    recipients = []
                    for recipient in template.default_recipients.all():
                        recipient = recipient.content_object
                        if isinstance(recipient, Group):
                            recipients += recipient.user_set.all().values_list("email")[0]
                        else:
                            recipients.append(recipient.email)
                    template.send(self.request, recipients, {"device": device, "user": self.request.user})
                if len(templates) == 1:
                    messages.success(self.request, _('Mail successfully sent'))
                else:
                    messages.success(self.request, _('Mails successfully sent'))
            if form.cleaned_data["room"]:
                reversion.set_comment(_("Device lent to {0} and moved to room {1}")
                                      .format(form.cleaned_data['owner'], device.room))
            else:
                reversion.set_comment(_("Device lent to {0}")
                                      .format(form.cleaned_data['owner']))
            lending.device = form.cleaned_data["device"]
        else:
            lending.smalldevice = form.cleaned_data["smalldevice"]
        lending.owner = get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)
        lending.duedate = form.cleaned_data["duedate"]
        lending.save()
        messages.success(self.request, _('Device is marked as lend to {0}').format(
            get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)))
        if form.cleaned_data["device"]:
            device.currentlending = lending
            device.save()
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))
        else:
            return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": lending.owner.pk}))


@permission_required('devices.change_device', raise_exception=True)
class DeviceInventoried(View):
    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        device.inventoried = timezone.now()
        device.save()
        messages.success(request, _('Device is marked as inventoried.'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))

    def post(self, request, **kwargs):
        return self.get(request, **kwargs)


@permission_required('devices.lend_device', raise_exception=True)
class DeviceReturn(FormView):
    template_name = 'devices/base_form.html'
    form_class = ReturnForm

    def get_context_data(self, **kwargs):
        context = super(DeviceReturn, self).get_context_data(**kwargs)
        context['actionstring'] = "Mark device as returned"

        # get lending object with given pk
        lending = get_object_or_404(Lending, pk=self.kwargs["lending"])

        if lending.device:
            device_name = lending.device.name
        else:
            device_name = lending.smalldevice
            del context["form"].fields["room"]

        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            ("", _("Return {0}").format(device_name))]
        return context

    def form_valid(self, form):
        device = None
        owner = None
        templates = []
        lending = get_object_or_404(Lending, pk=self.kwargs["lending"])
        if lending.device and lending.device != "":
            device = lending.device
            device.currentlending = None
            try:
                templates.append(MailTemplate.objects.get(usage="returned"))
            except:
                messages.error(self.request, _('MAIL NOT SENT - Template for returned device does not exist for your main department'))
            if form.cleaned_data["room"]:
                device.room = form.cleaned_data["room"]
                try:
                    templates.append(MailTemplate.objects.get(usage="room"))
                except:
                    messages.error(self.request, _('MAIL NOT SENT - Template for room change does not exist for your main department'))
            if templates:
                for template in templates:
                    recipients = []
                    for recipient in template.default_recipients.all():
                        recipient = recipient.content_object
                        if isinstance(recipient, Group):
                            recipients += recipient.user_set.all().values_list("email")[0]
                        else:
                            recipients.append(recipient.email)
                    template.send(self.request, recipients, {"device": device, "user": self.request.user})
                if len(templates) == 1:
                    messages.success(self.request, _('Mail successfully sent'))
                else:
                    messages.success(self.request, _('Mails successfully sent'))
            if form.cleaned_data["room"]:
                reversion.set_comment(_("Device returned and moved to room {0}").format(device.room))
            device.save()
        else:
            owner = lending.owner
        lending.returndate = datetime.date.today()
        lending.save()
        messages.success(self.request, _('Device is marked as returned'))
        if device is not None:
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))
        else:
            return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": owner.pk}))


@permission_required('devices.lend_device', raise_exception=True)
class DeviceMail(FormView):
    template_name = 'devices/base_form.html'
    form_class = DeviceMailForm

    def get_context_data(self, **kwargs):
        context = super(DeviceMail, self).get_context_data(**kwargs)

        # Add in a QuerySet of all the books
        context['form_scripts'] = "$('#id_owner').select2();"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": self.device.pk}), self.device.name),
            ("", _("Send Mail"))]
        return context

    def get_initial(self):
        deviceid = self.kwargs["pk"]
        self.device = get_object_or_404(Device, pk=deviceid)
        return {}

    def form_valid(self, form):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        template = form.cleaned_data["mailtemplate"]
        recipients = []
        for recipient in form.cleaned_data["emailrecipients"]:
            if recipient[0] == "g":
                group = get_object_or_404(Group, pk=recipient[1:])
                recipients += group.user_set.all().values_list("email")[0]
            else:
                recipients.append(get_object_or_404(Lageruser, pk=recipient[1:]).email)
        recipients = list(set(recipients))
        template.subject = form.cleaned_data["emailsubject"]
        template.body = form.cleaned_data["emailbody"]
        template.send(self.request, recipients, {"device": device, "user": self.request.user})
        if template.usage == "reminder" or template.usage == "overdue":
            device.currentlending.duedate_email = datetime.date.today()
            device.currentlending.save()
        messages.success(self.request, _('Mail successfully sent'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


@permission_required('devices.change_device', raise_exception=True)
class DeviceArchive(SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Device
    template_name = 'devices/device_archive.html'

    def post(self, request, **kwargs):
        device = self.get_object()
        if device.archived is None:
            device.archived = datetime.datetime.utcnow().replace(tzinfo=utc)
            device.room = None
            device.currentlending = None
            for ip in device.ipaddress_set.all():
                ip.device = None
                ip.save()
        else:
            device.archived = None
        device.save()
        reversion.set_comment(_("Device was archived".format(device.name)))
        messages.success(request, _("Device was archived."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


@permission_required('devices.change_device', raise_exception=True)
class DeviceTrash(SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Device
    template_name = 'devices/device_trash.html'

    def post(self, request, **kwargs):
        device = self.get_object()
        if device.trashed is None:
            device.trashed = datetime.datetime.utcnow().replace(tzinfo=utc)
            device.room = None
            if device.currentlending:
                device.currentlending.returndate = datetime.date.today()
                device.currentlending.save()
                device.currentlending = None
            # if device.uses
            if Device.objects.filter(used_in=device.pk):
                other_list = Device.objects.filter(used_in=device.pk)
                for element in other_list:
                    other = element
                    other.used_in = None
                    other.save()
            if device.used_in:
                device.used_in = None
            for ip in device.ipaddress_set.all():
                ip.device = None
                ip.save()

            try:
                template = MailTemplate.objects.get(usage="trashed")
            except:
                template = None
                messages.error(self.request, _('MAIL NOT SENT - Template for trashed device does not exist for this department'))
            if template is not None:
                recipients = []
                for recipient in template.default_recipients.all():
                    recipient = recipient.content_object
                    if isinstance(recipient, Group):
                        recipients += recipient.user_set.all().values_list("email")[0]
                    else:
                        recipients.append(recipient.email)
                template.send(self.request, recipients, {"device": device, "user": self.request.user})
                messages.success(self.request, _('Mail successfully sent'))
        else:
            device.trashed = None
        device.save()

        reversion.set_comment(_("Device was trashed".format(device.name)))
        messages.success(request, _("Device was trashed."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


@permission_required('devices.change_device', raise_exception=True)
class DeviceStorage(SingleObjectMixin, FormView):
    model = Device
    form_class = DeviceStorageForm
    template_name = 'devices/device_storage.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(DeviceStorage, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        device = self.get_object()
        try:
            if device.department:
                dep = device.department.name
            else:
                dep = "all"
            roomid = settings.STORAGE_ROOM[dep]
            room = get_object_or_404(Room, id=roomid)
        except:
            messages.error(self.request,
                           _("Could not move to storage. No room specified. Please contact your administrator."))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))
        device.room = room
        device.save()
        for ipaddress in device.ipaddress_set.all():
            ipaddress.device = None
            ipaddress.save()
        if form.cleaned_data["send_mail"]:
            try:
                template = MailTemplate.objects.get(usage="room")
            except:
                template = None
                messages.error(self.request, _('MAIL NOT SENT - Template for room change does not exist'))
            if template is not None:
                recipients = []
                for recipient in template.default_recipients.all():
                    recipient = recipient.content_object
                    if isinstance(recipient, Group):
                        recipients += recipient.user_set.all().values_list("email")[0]
                    else:
                        recipients.append(recipient.email)
                template.send(self.request, recipients, {"device": device, "user": self.request.user})
                messages.success(self.request, _('Mail successfully sent'))

        messages.success(self.request, _("Device was moved to storage."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


@permission_required('devices.read_device', raise_exception=True)
class DeviceBookmark(SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Device

    def post(self, request, **kwargs):
        device = self.get_object()
        if device.bookmarkers.filter(id=request.user.id).exists():
            bookmark = Bookmark.objects.get(user=request.user, device=device)
            bookmark.delete()
            messages.success(request, _("Bookmark was removed"))
        else:
            bookmark = Bookmark(device=device, user=request.user)
            bookmark.save()
            messages.success(request, _("Device was bookmarked."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


class TemplateList(PaginationMixin, ListView):
    model = Template
    context_object_name = 'template_list'

    def get_context_data(self, **kwargs):
        context = super(TemplateList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("template-list"), _("Templates")), ]

        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class TemplateCreate(CreateView):
    model = Template
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(TemplateCreate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("template-list"), _("Templates")),
            ("", _("Create new devicetemplate"))]
        return context


class TemplateUpdate(UpdateView):
    model = Template
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(TemplateUpdate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("template-list"), _("Templates")),
            ("", _("Edit: {0}".format(self.object.templatename)))]
        return context


class TemplateDelete(DeleteView):
    model = Template
    success_url = reverse_lazy('device-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("template-list"), _("Templates")),
            ("", _("Delete: {0}".format(self.object.templatename)))]
        return context


class RoomList(PaginationMixin, ListView):
    model = Room
    context_object_name = 'room_list'

    def get_queryset(self):
        rooms = Room.objects.select_related("building").all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            rooms = rooms.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            rooms = rooms.order_by(self.viewsorting)
        return rooms

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("room-list"), _("Rooms"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class RoomDetail(DetailView):
    model = Room
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Room.objects.exclude(pk=context["room"].pk).order_by("name").values("id", "name",
                                                                                                    "building__name")
        context['device_list'] = Device.objects.select_related().filter(room=context["room"], archived=None,
                                                                        trashed=None).values("id", "name",
                                                                                             "inventorynumber",
                                                                                             "devicetype__name")

        if "room" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["room"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(
                        context["room"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute,
                                                                                              getattr(context["room"],
                                                                                                      attribute))

        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk": context["room"].pk}), context["room"].name)]
        return context


class RoomCreate(CreateView):
    model = Room
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Room"
        context['type'] = "room"
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            ("", _("Create new room"))]
        return context


class RoomUpdate(UpdateView):
    model = Room
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Edit"))]
        return context


class RoomDelete(DeleteView):
    model = Room
    success_url = reverse_lazy('room-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context


class RoomMerge(View):
    model = Room

    def get(self, request, *args, **kwargs):
        context = {"oldobject": get_object_or_404(self.model, pk=kwargs["oldpk"]),
                   "newobject": get_object_or_404(self.model, pk=kwargs["newpk"])}
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render(request, 'devices/base_merge.html', context)

    @atomic
    def post(self, request, *args, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        devices = Device.objects.filter(room=oldobject)
        for device in devices:
            device.room = newobject
            reversion.set_comment(_("Merged Room {0} into {1}".format(oldobject, newobject)))
            device.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())


class BuildingList(PaginationMixin, ListView):
    model = Building
    context_object_name = 'building_list'

    def get_queryset(self):
        buildings = Building.objects.all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            buildings = buildings.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            buildings = buildings.order_by(self.viewsorting)
        return buildings

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("building-list"), _("Buildings"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        return context


class BuildingDetail(DetailView):
    model = Building
    context_object_name = 'building'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Building.objects.exclude(pk=context["building"].pk).order_by("name")
        context['device_list'] = Device.objects.select_related().filter(room__building=context["building"],
                                                                        archived=None, trashed=None).values("id",
                                                                                                            "name",
                                                                                                            "inventorynumber",
                                                                                                            "devicetype__name",
                                                                                                            "room__name")

        if "building" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["building"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(
                        context["building"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(
                        context["building"], attribute))

        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk": context["building"].pk}), context["building"].name)]
        return context


class BuildingCreate(CreateView):
    model = Building
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Building"
        context['type'] = "building"
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            ("", _("Create new building"))]
        return context


class BuildingUpdate(UpdateView):
    model = Building
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Edit"))]
        return context


class BuildingDelete(DeleteView):
    model = Building
    success_url = reverse_lazy('building-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context


class BuildingMerge(View):
    model = Building

    def get(self, request, *args, **kwargs):
        context = {"oldobject": get_object_or_404(self.model, pk=kwargs["oldpk"]),
                   "newobject": get_object_or_404(self.model, pk=kwargs["newpk"])}
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render(request, 'devices/base_merge.html', context)

    @atomic
    def post(self, request, *args, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        rooms = Room.objects.filter(building=oldobject)
        for room in rooms:
            room.building = newobject
            room.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())


class ManufacturerList(PaginationMixin, ListView):
    model = Manufacturer
    context_object_name = 'manufacturer_list'

    def get_queryset(self):
        manufacturers = Manufacturer.objects.all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            manufacturers = manufacturers.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            manufacturers = manufacturers.order_by(self.viewsorting)
        return manufacturers

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("manufacturer-list"), _("Manufacturers"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class ManufacturerDetail(DetailView):
    model = Manufacturer
    context_object_name = 'object'
    template_name = "devices/manufacturer_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Manufacturer.objects.exclude(pk=context["object"].pk).order_by("name")
        context['device_list'] = Device.objects.filter(manufacturer=context["object"], archived=None,
                                                       trashed=None).values("id", "name", "inventorynumber",
                                                                            "devicetype__name", "room__name",
                                                                            "room__building__name")

        if "manufacturer" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["manufacturer"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(
                        context["manufacturer"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(
                        context["manufacturer"], attribute))

        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            (reverse("manufacturer-detail", kwargs={"pk": context["object"].pk}), context["object"].name)]
        return context


class ManufacturerCreate(CreateView):
    model = Manufacturer
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Manufacturer"
        context['type'] = "manufacturer"
        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            ("", _("Create new manufacturer"))]
        return context


class ManufacturerUpdate(UpdateView):
    model = Manufacturer
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            (reverse("manufacturer-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Edit"))]
        return context


class ManufacturerDelete(DeleteView):
    model = Manufacturer
    success_url = reverse_lazy('manufacturer-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            (reverse("manufacturer-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context


class ManufacturerMerge(View):
    model = Manufacturer

    def get(self, request, *args, **kwargs):
        context = {"oldobject": get_object_or_404(self.model, pk=kwargs["oldpk"]),
                   "newobject": get_object_or_404(self.model, pk=kwargs["newpk"])}
        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            (reverse("manufacturer-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render(request, 'devices/base_merge.html', context)

    @atomic
    def post(self, request, *args, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        devices = Device.objects.filter(manufacturer=oldobject)
        for device in devices:
            device.manufacturer = newobject
            reversion.set_comment(_("Merged Manufacturer {0} into {1}".format(oldobject, newobject)))
            device.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())


class NoteCreate(CreateView):
    model = Note
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_initial(self):
        initial = super(NoteCreate, self).get_initial()
        initial["device"] = get_object_or_404(Device, pk=self.kwargs["pk"])
        initial["creator"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super(NoteCreate, self).get_context_data(**kwargs)
        device = get_object_or_404(Device, pk=self.kwargs["pk"])
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": device.pk}), device),
            ("", _("Notes")),
            ("", _("Create new note"))]
        return context


class NoteUpdate(UpdateView):
    model = Note
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy("device-detail", kwargs={"pk": self.object.device.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NoteUpdate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["object"].device.pk}), context["object"].device.name),
            ("", _("Edit"))]
        return context


class NoteDelete(DeleteView):
    model = Note
    template_name = 'devices/base_delete.html'

    def get_success_url(self):
        return reverse_lazy("device-detail", kwargs={"pk": self.object.device.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NoteDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["object"].device.pk}), context["object"].device.name),
            ("", _("Delete"))]
        return context


class PictureCreate(CreateView):
    model = Picture
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_initial(self):
        initial = super(PictureCreate, self).get_initial()
        initial["device"] = get_object_or_404(Device, pk=self.kwargs["pk"])
        initial["creator"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super(PictureCreate, self).get_context_data(**kwargs)
        device = get_object_or_404(Device, pk=self.kwargs["pk"])
        context["enctype"] = "multipart/form-data"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": device.pk}), device),
            ("", _("Notes")),
            ("", _("Create new note"))]
        return context


class PictureUpdate(UpdateView):
    model = Picture
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy("device-detail", kwargs={"pk": self.object.device.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PictureUpdate, self).get_context_data(**kwargs)
        context["enctype"] = "multipart/form-data"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["object"].device.pk}), context["object"].device.name),
            ("", _("Edit"))]
        return context


class PictureDelete(DeleteView):
    model = Picture
    template_name = 'devices/base_delete.html'

    def get_success_url(self):
        return reverse_lazy("device-detail", kwargs={"pk": self.object.device.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PictureDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["object"].device.pk}), context["object"].device.name),
            ("", _("Delete"))]
        return context


class Search(ListView):
    model = Device
    template_name = 'devices/search.html'

    STRING_FIELDS = {
        'name': 'name',
        'inventorynumber': 'inventorynumber',
        'serialnumber': 'serialnumber',
        'hostname': 'hostname',
        'description': 'description',
        'manufacturer': 'manufacturer__name',
        'room': 'room__name',
        'building': 'room__building__name',
        'type': 'devicetype__name',
        'group': 'group__name',
        'contact': 'contact__username',
        'department': 'department__name',
        'tag': 'tags__name',
        'user': 'currentlending__owner__username',
    }
    DATE_FIELDS = {
        'archived': 'archived',
        'trashed': 'trashed',
        'inventoried': 'inventoried',
    }

    def get_searchstring(self):
        return self.request.GET.get('searchstring', '')

    def parse_searchstring(self, searchstring):
        """
        Example:

            `foo "foo bar" baz:2`
            [(None, 'foo'), (None, 'foo bar'), ('baz', '2')]
        """

        in_string = False
        key = ''
        token = ''
        for c in searchstring + ' ':
            if in_string:
                if c == '"':
                    in_string = False
                else:
                    token += c
            else:
                if c == '"':
                    in_string = True
                elif c == ' ':
                    if key:
                        yield key, token
                        key = ''
                        token = ''
                    elif token:
                        yield None, token
                        token = ''
                elif c == ':' and not key:
                    key = token
                    token = ''
                else:
                    token += c

    def parse_boolean(self, s):
        return s.lower() in ['', '0', 'false', 'no']

    def get_q(self):
        data = {}
        for key, value in self.parse_searchstring(self.get_searchstring()):
            if key not in data:
                data[key] = []
            data[key].append(value)

        result = models.Q()
        for key, values in data.items():
            if key is None:
                for value in values:
                    q = models.Q()
                    for k in self.STRING_FIELDS.values():
                        q |= models.Q(**{k + '__icontains': value})
                    result &= q
            elif key in self.STRING_FIELDS:
                k = self.STRING_FIELDS[key] + '__icontains'

                q = models.Q()
                for value in values:
                    q |= models.Q(**{k: value})
                result &= q
            elif key in self.DATE_FIELDS:
                k = self.DATE_FIELDS[key] + '__isnull'

                q = models.Q()
                for value in values:
                    q |= models.Q(**{k: self.parse_boolean(value)})
                result &= q
            else:
                raise SuspiciousOperation(_('Invalid search'))
        return result

    def get_queryset(self):
        return Device.objects.filter(self.get_q())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Search, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [("", _("Search"))]
        context["searchstring"] = self.get_searchstring()
        context["keys"] = sorted(list(self.STRING_FIELDS.keys()) +
            list(self.DATE_FIELDS.keys()))
        return context


class PublicDeviceListView(ListView):
    filterstring = ""
    groupfilter = None
    viewsorting = None
    template_name = "devices/public_devices_list.html"

    def get_queryset(self):
        query_dict = settings.PUBLIC_DEVICES_FILTER
        if len(query_dict) == 0:
            raise ImproperlyConfigured

        devices = Device.objects.filter(**query_dict)
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            devices = devices.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devices = devices.order_by(self.viewsorting)
        self.groupfilter = self.kwargs.pop("group", "all")
        if self.groupfilter != "all":
            devices = devices.filter(group__id=self.groupfilter)
        return devices.values("id", "name", "inventorynumber", "devicetype__name", "room__name",
                                  "room__building__name",
                                  "group__name", "currentlending__owner__username", "currentlending__duedate")

    def get_context_data(self, **kwargs):
        context = super(PublicDeviceListView, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("public-device-list"), _("Public Devices"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        context["groupfilterform"] = DeviceGroupFilterForm(initial={"groupfilter": self.groupfilter})
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        context["nochrome"] = self.request.GET.get("nochrome", False)
        return context


class PublicDeviceDetailView(DetailView):
    template_name = "devices/device_detail.html"
    context_object_name = "device"

    def get_queryset(self):
        query_dict = settings.PUBLIC_DEVICES_FILTER
        if len(query_dict) == 0:
            raise ImproperlyConfigured

        devices = Device.objects.prefetch_related("room", "room__building", "manufacturer", "devicetype").filter(
            **query_dict)
        devices = devices.filter(id=self.kwargs.get("pk", None))
        if devices.count() != 1:
            raise Http404

        return devices

    def get_context_data(self, **kwargs):
        context = super(PublicDeviceDetailView, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("public-device-list"), _("Public Devices")),
            (reverse("public-device-detail", kwargs={"pk": context["device"].pk}), context["device"].name)]
        context["nochrome"] = self.request.GET.get("nochrome", False)
        return context
