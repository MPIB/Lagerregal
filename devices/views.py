# coding: utf-8
import datetime

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, FormView, TemplateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView, SingleObjectMixin
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import Group
from django.shortcuts import render_to_response
from reversion.models import Version
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.timezone import utc
from django.utils import timezone
import reversion
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import commit_on_success
from django.conf import settings

from devices.models import Device, Template, Room, Building, Manufacturer, Lending, Note, Bookmark
from devicetypes.models import TypeAttribute, TypeAttributeValue
from network.models import IpAddress
from mail.models import MailTemplate, MailHistory
from devices.forms import IpAddressForm, SearchForm, LendForm, DeviceViewForm, IpAddressPurposeForm
from devices.forms import ViewForm, DeviceForm, DeviceMailForm, VIEWSORTING, VIEWSORTING_DEVICES, FilterForm, \
    DeviceStorageForm, ReturnForm
from devicetags.forms import DeviceTagForm
from users.models import Lageruser
from Lagerregal.utils import PaginationMixin
from devicetags.models import Devicetag


class DeviceList(PaginationMixin, ListView):
    context_object_name = 'device_list'
    viewfilter = None
    viewsorting = None

    def get_queryset(self):
        self.viewfilter = self.kwargs.pop("filter", "active")
        devices = None
        if self.viewfilter == "all":
            devices = Device.objects.all()
        elif self.viewfilter == "available":
            devices = Device.active().filter(currentlending=None)
        elif self.viewfilter == "lent":
            devices = Device.objects.exclude(currentlending=None)
        elif self.viewfilter == "archived":
            devices = Device.objects.exclude(archived=None)
        elif self.viewfilter == "trashed":
            devices = Device.objects.exclude(trashed=None)
        elif self.viewfilter == "overdue":
            devices = Device.objects.filter(currentlending__duedate__lt=datetime.date.today())
        elif self.viewfilter == "returnsoon":
            soon = datetime.date.today() + datetime.timedelta(days=10)
            devices = Device.objects.filter(currentlending__duedate__lte=soon,
                                            currentlending__duedate__gt=datetime.date.today())
        elif self.viewfilter == "temporary":
            devices = Device.active().filter(templending=True)
        elif self.viewfilter == "bookmark":
            if self.request.user.is_authenticated:
                devices = self.request.user.bookmarks.all()
        else:
            devices = Device.active()
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING_DEVICES]:
            devices = devices.order_by(self.viewsorting)

        return devices.values("id", "name", "inventorynumber", "devicetype__name", "room__name", "room__building__name",
                              "group__name", "currentlending__owner__username", "currentlending__duedate")

    def get_context_data(self, **kwargs):
        context = super(DeviceList, self).get_context_data(**kwargs)
        context["viewform"] = DeviceViewForm(initial={'viewfilter': self.viewfilter, "viewsorting": self.viewsorting})
        context["template_list"] = Template.objects.all()
        context["viewfilter"] = self.viewfilter
        context["breadcrumbs"] = [[reverse("device-list"), _("Devices")]]
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class DeviceDetail(DetailView):
    queryset = Device.objects.select_related("manufacturer", "devicetype", "currentlending")
    context_object_name = 'device'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['ipaddressform'] = IpAddressForm()
        context['tagform'] = DeviceTagForm()
        context['tagform'].fields["tags"].queryset = Devicetag.objects.exclude(devices=context["device"])
        context["lending_list"] = Lending.objects.filter(device=context["device"]).order_by("-pk")[:10]
        context["version_list"] = Version.objects.filter(object_id=context["device"].id,
                                                         content_type_id=ContentType.objects.get(
                                                             model='device').id).order_by("-pk")[:10]
        context["mail_list"] = MailHistory.objects.filter(device=context["device"]).order_by("-pk")[:10]
        context["today"] = datetime.datetime.utcnow().replace(tzinfo=utc)
        context["weekago"] = context["today"] - datetime.timedelta(days=7)
        context["attributevalue_list"] = TypeAttributeValue.objects.filter(device=context["device"])
        context["lendform"] = LendForm()
        mailinitial = {}
        if context["device"].currentlending is not None:
            currentowner = context["device"].currentlending.owner
            mailinitial["owner"] = currentowner
            mailinitial["emailrecipients"] = ("u" + str(currentowner.id), currentowner.username)
        try:
            mailinitial["mailtemplate"] = MailTemplate.objects.get(usage="reminder")
            mailinitial["emailsubject"] = mailinitial["mailtemplate"].subject
            mailinitial["emailbody"] = mailinitial["mailtemplate"].body
        except:
            pass
        context["mailform"] = DeviceMailForm(initial=mailinitial)
        versions = reversion.get_for_object(context["device"])
        if len(versions) != 0:
            context["lastedit"] = versions[0]

        if "device" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["device"][1]:
                if attribute == "id":
                    context["label_js"] += u"\nlabel.setObjectText('{0}', '{1:07d}');".format(attribute,
                                                                                              getattr(context["device"],
                                                                                                      attribute))
                else:
                    context["label_js"] += u"\nlabel.setObjectText('{0}', '{1}');".format(attribute,
                                                                                          getattr(context["device"],
                                                                                                  attribute))

        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name)]
        return context


class DeviceIpAddressRemove(DeleteView):
    template_name = 'devices/unassign_ipaddress.html'
    model = IpAddress

    def get(self, request, *args, **kwargs):
        context = {"device": get_object_or_404(Device, pk=kwargs["pk"]),
                   "ipaddress": get_object_or_404(IpAddress, pk=kwargs["ipaddress"])}
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name),
            ("", _("Unassign IP-Addresses"))]
        return render_to_response(self.template_name, context, RequestContext(request))

    def post(self, request, *args, **kwargs):
        device = get_object_or_404(Device, pk=kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        ipaddress.device = None
        ipaddress.purpose = None
        reversion.set_comment(_("Removed from Device {0}".format(device.name)))
        ipaddress.save()

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


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
        try:
            initial["emailtemplate"] = MailTemplate.objects.get(usage="new")
            initial["emailrecipients"] = [obj.content_type.name[0].lower() + str(obj.object_id) for obj in
                                          initial["emailtemplate"].default_recipients.all()]
            initial["emailsubject"] = initial["emailtemplate"].subject
            initial["emailbody"] = initial["emailtemplate"].body
        except:
            pass
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Device"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            ("", _("Create new device"))]
        return context

    def form_valid(self, form):
        form.cleaned_data["creator"] = self.request.user
        reversion.set_comment(_("Created"))
        r = super(DeviceCreate, self).form_valid(form)
        for key, value in form.cleaned_data.iteritems():
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
                    recipients += group.lageruser_set.all().values_list("email")[0]
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

        messages.success(self.request, _('Device was successfully created.'))
        return r


class DeviceUpdate(UpdateView):
    model = Device
    template_name = 'devices/device_form.html'
    form_class = DeviceForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name),
            ("", _("Edit"))]
        context["template_list"] = MailTemplate.objects.exclude(usage=None)
        return context

    def form_valid(self, form):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived is not None:
            messages.error(self.request, _("Archived Devices can't be edited"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))

        if form.cleaned_data["comment"] == "":
            reversion.set_comment(_("Updated"))
        else:
            reversion.set_comment(form.cleaned_data["comment"])
        reversion.set_ignore_duplicates(True)

        if device.devicetype is not None:
            if form.cleaned_data["devicetype"] is None or device.devicetype.pk != form.cleaned_data["devicetype"].pk:
                TypeAttributeValue.objects.filter(device=device.pk).delete()
        for key, value in form.cleaned_data.iteritems():
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
                    recipients += group.lageruser_set.all().values_list("email")[0]
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


        messages.success(self.request, _('Device was successfully updated.'))
        return super(DeviceUpdate, self).form_valid(form)


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


class DeviceLend(FormView):
    template_name = 'devices/base_form.html'
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
                    (reverse("device-detail", kwargs={"pk": device.pk}), device.name),
                    ("", _("Lend"))]
                return context

        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            ("", _("Lend"))]
        return context

    def form_valid(self, form):
        lending = Lending()
        device = None
        if form.cleaned_data["device"] and form.cleaned_data["device"] != "":
            device = form.cleaned_data["device"]
            if device.archived is not None:
                messages.error(self.request, _("Archived Devices can't be lent"))
                return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))

            if form.cleaned_data["room"]:
                device.room = form.cleaned_data["room"]
                try:
                    template = MailTemplate.objects.get(usage="room")
                except:
                    template = None
                if not template == None:
                    recipients = []
                    for recipient in template.default_recipients.all():
                        recipient = recipient.content_object
                        if isinstance(recipient, Group):
                            recipients += recipient.lageruser_set.all().values_list("email")[0]
                        else:
                            recipients.append(recipient.email)
                    template.send(self.request, recipients, {"device": device, "user": self.request.user})
                    messages.success(self.request, _('Mail successfully sent'))
                reversion.set_comment(_("Device lent and moved to room {0}").format(device.room))
            lending.device = form.cleaned_data["device"]
        else:
            lending.smalldevice = form.cleaned_data["smalldevice"]
        lending.owner = get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)
        lending.duedate = form.cleaned_data["duedate"]
        lending.save()
        reversion.set_ignore_duplicates(True)
        messages.success(self.request, _('Device is marked as lend to {0}').format(
            get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)))
        if form.cleaned_data["device"]:
            device.currentlending = lending
            device.save()
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))
        else:
            return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": lending.owner.pk}))


class DeviceInventoried(View):
    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        device.inventoried = timezone.now()
        device.save()
        reversion.set_ignore_duplicates(True)
        messages.success(request, _('Device is marked as inventoried.'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))

    def post(self, request, **kwargs):
        return self.get(request, **kwargs)


class DeviceReturn(FormView):
    template_name = 'devices/base_form.html'
    form_class = ReturnForm

    def get_context_data(self, **kwargs):
        context = super(DeviceReturn, self).get_context_data(**kwargs)
        context['actionstring'] = "Mark device as returned"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            ("", _("Return"))]
        return context

    def form_valid(self, form):
        device = None
        owner = None
        lending = get_object_or_404(Lending, pk=self.kwargs["lending"])
        if lending.device and lending.device != "":
            device = lending.device
            device.currentlending = None
            device.save()
            if form.cleaned_data["room"]:
                device.room = form.cleaned_data["room"]
                try:
                    template = MailTemplate.objects.get(usage="room")
                except:
                    template = None
                if not template == None:
                    recipients = []
                    for recipient in template.default_recipients.all():
                        recipient = recipient.content_object
                        if isinstance(recipient, Group):
                            recipients += recipient.lageruser_set.all().values_list("email")[0]
                        else:
                            recipients.append(recipient.email)
                    template.send(self.request, recipients, {"device": device, "user": self.request.user})
                    messages.success(self.request, _('Mail successfully sent'))
                reversion.set_comment(_("Device returned and moved to room {0}").format(device.room))
        else:
            owner = lending.owner
        lending.returndate = datetime.datetime.now()
        lending.save()
        reversion.set_ignore_duplicates(True)
        messages.success(self.request, _('Device is marked as returned'))
        if device != None:
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))
        else:
            return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": owner.pk}))


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
                recipients += group.lageruser_set.all().values_list("email")[0]
            else:
                recipients.append(get_object_or_404(Lageruser, pk=recipient[1:]).email)
        recipients = list(set(recipients))
        template.subject = form.cleaned_data["emailsubject"]
        template.body = form.cleaned_data["emailbody"]
        template.send(self.request, recipients, {"device": device, "user": self.request.user})
        if template.usage == "reminder" or template.usage == "overdue":
            device.currentlending.duedate_email = datetime.datetime.utcnow().replace(tzinfo=utc)
            device.currentlending.save()
        messages.success(self.request, _('Mail successfully sent'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


class DeviceArchive(SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Device
    template_name = 'devices/device_archive.html'

    def post(self, request, **kwargs):
        device = self.get_object()
        if device.archived == None:
            device.archived = datetime.datetime.utcnow().replace(tzinfo=utc)
            device.room = None
            device.currentlending = None
            for ip in device.ipaddress_set.all():
                ip.device = None
                ip.save()
        else:
            device.archived = None
        device.save()
        #reversion.set_comment("Archived")
        reversion.set_ignore_duplicates(True)
        reversion.set_comment(_("Device was archived".format(device.name)))
        messages.success(request, _("Device was archived."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


class DeviceTrash(SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Device
    template_name = 'devices/device_trash.html'

    def post(self, request, **kwargs):
        device = self.get_object()
        if device.trashed == None:
            device.trashed = datetime.datetime.utcnow().replace(tzinfo=utc)
            device.room = None
            device.currentlending = None
            for ip in device.ipaddress_set.all():
                ip.device = None
                ip.save()

            try:
                template = MailTemplate.objects.get(usage="trashed")
            except:
                template = None
            if not template == None:
                recipients = []
                for recipient in template.default_recipients.all():
                    recipient = recipient.content_object
                    if isinstance(recipient, Group):
                        recipients += recipient.lageruser_set.all().values_list("email")[0]
                    else:
                        recipients.append(recipient.email)
                template.send(self.request, recipients, {"device": device, "user": self.request.user})
                messages.success(self.request, _('Mail successfully sent'))
        else:
            device.trashed = None
        device.save()
        #reversion.set_comment("Archived")
        reversion.set_ignore_duplicates(True)
        reversion.set_comment(_("Device was trashed".format(device.name)))
        messages.success(request, _("Device was trashed."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


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
            roomid = settings.STORAGE_ROOM
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
            if not template == None:
                recipients = []
                for recipient in template.default_recipients.all():
                    recipient = recipient.content_object
                    if isinstance(recipient, Group):
                        recipients += recipient.lageruser_set.all().values_list("email")[0]
                    else:
                        recipients.append(recipient.email)
                template.send(self.request, recipients, {"device": device, "user": self.request.user})
                messages.success(self.request, _('Mail successfully sent'))
        reversion.set_ignore_duplicates(True)
        messages.success(self.request, _("Device was moved to storage."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


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

    def get(self, request, **kwargs):
        context = {"oldobject": get_object_or_404(self.model, pk=kwargs["oldpk"]),
                   "newobject": get_object_or_404(self.model, pk=kwargs["newpk"])}
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    @commit_on_success
    def post(self, request, **kwargs):
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

    def get(self, request, **kwargs):
        context = {"oldobject": get_object_or_404(self.model, pk=kwargs["oldpk"]),
                   "newobject": get_object_or_404(self.model, pk=kwargs["newpk"])}
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    @commit_on_success
    def post(self, request, **kwargs):
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

    def get(self, request, **kwargs):
        context = {"oldobject": get_object_or_404(self.model, pk=kwargs["oldpk"]),
                   "newobject": get_object_or_404(self.model, pk=kwargs["newpk"])}
        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            (reverse("manufacturer-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    @commit_on_success
    def post(self, request, **kwargs):
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


class Search(TemplateView):
    template_name = 'devices/search.html'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Search, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [("", _("Search"))]
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        searchlist = self.request.POST["searchname"].split(" ")
        for i, item in enumerate(searchlist):
            if "." in item:
                is_ip = True
                for element in item.split("."):
                    try:
                        intelement = int(element)
                        if not (0 <= intelement <= 255):
                            is_ip = False
                    except:
                        is_ip = False
                if is_ip:
                    searchlist[i] = "ipaddress: " + item
            elif len(item) == 7:
                try:
                    int(item)
                    searchlist[i] = "id: " + item
                except:
                    pass
        context["searchterm"] = " ".join(searchlist)

        return render_to_response(self.template_name, context, RequestContext(self.request))
