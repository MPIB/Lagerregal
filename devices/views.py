from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, FormView, TemplateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy, reverse
from devices.models import Device, Template, Room, Building, Manufacturer, Lending, Note, Bookmark
from django.contrib.auth.models import Group
from devicetypes.models import Type, TypeAttribute, TypeAttributeValue
from network.models import IpAddress
from mail.models import MailTemplate, MailHistory
from django.shortcuts import render_to_response
from reversion.models import Version
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.formats import localize
from django.contrib import messages
from devices.forms import IpAddressForm, SearchForm, LendForm, DeviceViewForm
from devices.forms import ViewForm, DeviceForm, DeviceMailForm, VIEWSORTING, VIEWSORTING_DEVICES, FilterForm
import datetime
from django.utils.timezone import utc
import reversion
from django.contrib.auth.models import Permission
from users.models import Lageruser
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.transaction import commit_on_success
from django.conf import settings
from Lagerregal.utils import PaginationMixin

class DeviceList(PaginationMixin, ListView):
    context_object_name = 'device_list'

    def get_queryset(self):
        self.viewfilter = self.kwargs.pop("filter", "active")
        if self.viewfilter == "all":
            devices = Device.objects.all()
        elif self.viewfilter == "available":
            devices = Device.active().filter(currentlending=None)
        elif self.viewfilter == "lendt":
            devices = Device.objects.exclude(currentlending=None)
        elif self.viewfilter == "archived":
            devices = Device.objects.exclude(archived=None)
        elif self.viewfilter == "trashed":
            devices = Device.objects.exclude(trashed=None)
        elif self.viewfilter == "overdue":
            devices = Device.objects.filter(currentlending__duedate__lt = datetime.date.today())
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
        
        return devices.values("id", "name", "inventorynumber", "devicetype__name", "room__name", "room__building__name", "group__name", "currentlending")

    def get_context_data(self, **kwargs):
        context = super(DeviceList, self).get_context_data(**kwargs)
        context["viewform"] = DeviceViewForm(initial={'viewfilter': self.viewfilter, "viewsorting":self.viewsorting})
        context["template_list"] = Template.objects.all()
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
        context['ipaddress_list'] = IpAddress.objects.filter(device=context['device'])
        context['ipaddress_available'] = IpAddress.objects.filter(device=None)
        context['ipaddressform'] = IpAddressForm()
        context["lending_list"] = Lending.objects.filter(device=context["device"]).order_by("-pk")[:10]
        context["version_list"] = Version.objects.filter(object_id=context["device"].id, content_type_id=ContentType.objects.get(model='device').id).order_by("-pk")[:10]
        context["mail_list"] = MailHistory.objects.filter(device=context["device"]).order_by("-pk")[:10]
        context["today"] = datetime.datetime.utcnow().replace(tzinfo=utc)
        context["weekago"] = context["today"] - datetime.timedelta(days=7)
        context["attributevalue_list"] = TypeAttributeValue.objects.filter(device=context["device"])
        context["lendform"] = LendForm()
        context["notes"] = Note.objects.select_related("creator").filter(device=context["device"]).order_by("-id")
        
        mailinitial = {}
        if context["device"].currentlending != None:
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
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(context["device"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(context["device"], attribute))

        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":context["device"].pk}), context["device"].name)]
        return context

class DeviceIpAddressRemove(DeleteView):
    template_name = 'devices/unassign_ipaddress.html'
    model = IpAddress

    def get(self, request, *args, **kwargs):
        context = {}
        context["device"] = get_object_or_404(Device, pk=kwargs["pk"])
        context["ipaddress"] = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":context["device"].pk}), context["device"].name),
            ("", _("Unassign IP-Addresses"))]
        return render_to_response(self.template_name, context, RequestContext(request))


    def post(self, request, *args, **kwargs):
        device = get_object_or_404(Device, pk=kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        ipaddress.device = None
        ipaddress.save()

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))


class DeviceIpAddress(FormView):
    template_name = 'devices/assign_ipaddress.html'
    form_class = IpAddressForm
    success_url = "/devices"

    def get_context_data(self, **kwargs):
        context = super(DeviceIpAddress, self).get_context_data(**kwargs)
        device = context["form"].cleaned_data["device"]
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":device.pk}), device.name),
            ("", _("Assign IP-Addresses"))]
        return context

    def form_valid(self, form):
        ipaddresses = form.cleaned_data["ipaddresses"]
        device = form.cleaned_data["device"]
        if device.archived != None:
            messages.error(self.request, _("Archived Devices can't get new IP-Addresses"))
            return HttpResponseRedirect(self.reverse("device-detail", kwargs={"pk":device.pk}))
        for ipaddress in ipaddresses:
            ipaddress.device = device
            ipaddress.save()
        
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceHistory(View):

    def get(self, request, **kwargs):
        revisionid = kwargs["revision"]
        device = get_object_or_404(Device, pk=kwargs["pk"])
        this_version = get_object_or_404(Version,
            revision_id=revisionid,
            object_id=device.id,
            content_type_id=ContentType.objects.get(model='device').id)

        previous_version = Version.objects.filter(object_id=device.pk,
            revision__date_created__lt=this_version.revision.date_created,
            content_type_id=ContentType.objects.get(model='device').id).order_by("-pk")
        if len(previous_version) == 0:
            previous_version = None
            previouscomment=None
        else:
            revisionpk = previous_version[0].revision.pk
            previouscomment = previous_version[0].revision.comment
            previous_version = previous_version[0].field_dict
            previous_version["revisionpk"] = revisionpk
            if previous_version["devicetype"] != None:
                try:
                    previous_version["devicetype"] = Type.objects.get(pk=previous_version["devicetype"])
                except Type.DoesNotExist:
                    previous_version["devicetype"] = "[deleted]"
            if previous_version["manufacturer"] != None:
                try:
                    previous_version["manufacturer"] = Manufacturer.objects.get(pk=previous_version["manufacturer"])
                except Type.DoesNotExist:
                    previous_version["manufacturer"] = "[deleted]"
            if previous_version["room"] != None:
                try:
                    previous_version["room"] = Room.objects.get(pk=previous_version["room"])
                except Type.DoesNotExist:
                    previous_version["room"] = "[deleted]"

        next_version = Version.objects.filter(object_id=device.pk,
            revision__date_created__gt=this_version.revision.date_created,
            content_type_id=ContentType.objects.get(model='device').id).order_by("pk")
        if len(next_version) == 0:
            next_version = None
            nextcomment=None
        else:
            revisionpk = next_version[0].revision.pk
            nextcomment = next_version[0].revision.comment
            next_version = next_version[0].field_dict
            next_version["revisionpk"] = revisionpk

        if this_version.field_dict["devicetype"] != None:
            try:
                this_version.field_dict["devicetype"] = Type.objects.get(pk=this_version.field_dict["devicetype"])
            except Type.DoesNotExist:
                this_version.field_dict["devicetype"] = "[deleted]"
        if this_version.field_dict["manufacturer"] != None:
            try:
                this_version.field_dict["manufacturer"] = Manufacturer.objects.get(pk=this_version.field_dict["manufacturer"])
            except Type.DoesNotExist:
                this_version.field_dict["manufacturer"] = "[deleted]"
        if this_version.field_dict["room"] != None:
            try:
                this_version.field_dict["room"] = Room.objects.get(pk=this_version.field_dict["room"])
            except Type.DoesNotExist:
                this_version.field_dict["room"] = "[deleted]"
        context = {"version":this_version,
            "previous":previous_version,
            "previouscomment":previouscomment,
            "this_version":this_version.field_dict,
            "thiscomment":this_version.revision.comment,
            "current":device,
            "next":next_version,
            "nextcomment":nextcomment}
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":device.pk}), device.name),
            (reverse("device-history-list", kwargs={"pk":device.pk}), _("History")),
            ("", _("Version {0}".format(this_version.revision.pk)))
            ]
        return render_to_response('devices/device_history.html', context, RequestContext(request))

    def post(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(self.request, _("Archived Devices can't be reverted"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
        revisionid = kwargs["revision"]

        version = get_object_or_404(Version,
            revision_id=revisionid,
            object_id=deviceid,
            content_type_id=ContentType.objects.get(model='device').id)
        currentlending = device.currentlending
        archived = device.archived
        version.revision.revert()
        device = get_object_or_404(Device, pk=deviceid)
        device.currentlending = currentlending
        device.archived = archived
        
        deleted_keys = []

        try:
            devicetype = device.devicetype
        except Type.DoesNotExist:
            device.devicetype = None
            deleted_keys.append(ugettext("Devicetype"))

        try:
            manufacturer = device.manufacturer
        except Manufacturer.DoesNotExist:
            device.manufacturer = None
            deleted_keys.append(ugettext("Manufacturer"))

        try:
            room = device.room
        except Room.DoesNotExist:
            device.room = None
            deleted_keys.append(ugettext("Room"))

        device.save()
        if version.field_dict["devicetype"] != None:        
            TypeAttributeValue.objects.filter(device = version.object_id).delete()
        reversion.set_comment("Reverted to version from {0}".format(localize(version.revision.date_created)))
        reversion.set_ignore_duplicates(True)

        if deleted_keys == []:
            messages.success(self.request, _('Successfully reverted Device to revision {0}').format(version.revision.id))
        else:
            messages.warning(self.request, _("Reverted Device to revision {0}, but the following fields had to be set to null, as the referenced object was deleted: {1}").format(version.revision.id, ",".join(deleted_keys)))

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceHistoryList(ListView):
    context_object_name = 'version_list'
    template_name = 'devices/device_history_list.html'

    def get_queryset(self):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        return Version.objects.filter(object_id=device.id, content_type_id=ContentType.objects.get(model='device').id).order_by("-pk")

    def get_context_data(self, **kwargs):
        context = super(DeviceHistoryList, self).get_context_data(**kwargs)
        context["device"] = get_object_or_404(Device, pk=self.kwargs["pk"])
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":context["device"].pk}), context["device"].name),
            ("", _("History"))]
        return context

    

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
            (reverse("device-detail", kwargs={"pk":context["device"].pk}), context["device"].name),
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
        if templateid != None:
            initial += get_object_or_404(Template, pk=templateid).get_as_dict()
        copyid = self.kwargs.pop("copyid", None)
        if copyid != None:
            initial += get_object_or_404(Device, pk=copyid).get_as_dict()
            initial["deviceid"] = copyid
        initial["creator"] = creator
        try:
            initial["emailtemplate"] = MailTemplate.objects.get(usage="new")
            initial["emailrecipients"] = [obj.content_type.name[0].lower() + str(obj.object_id) for obj in initial["emailtemplate"].default_recipients.all()]
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
        if form.cleaned_data["comment"] == "":
            reversion.set_comment(_("Created"))
        else:
            reversion.set_comment(form.cleaned_data["comment"])
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
            template.send(request=self.request, recipients=recipients, data={"device":self.object, "user":self.request.user})

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
            (reverse("device-detail", kwargs={"pk":context["device"].pk}), context["device"].name),
            ("", _("Edit"))]
        context["template_list"] = MailTemplate.objects.exclude(usage=None)
        return context

    def form_valid(self, form):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(self.request, _("Archived Devices can't be edited"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

        if form.cleaned_data["comment"] == "":
            reversion.set_comment(_("Updated"))
        else:
            reversion.set_comment(form.cleaned_data["comment"])
        reversion.set_ignore_duplicates(True)

        if device.devicetype != None:
            if form.cleaned_data["devicetype"] == None or device.devicetype.pk != form.cleaned_data["devicetype"].pk:
                TypeAttributeValue.objects.filter(device = device.pk).delete()
        for key, value in form.cleaned_data.iteritems():
            if key.startswith("attribute_") and value != "":
                attributenumber = key.split("_")[1]
                typeattribute = get_object_or_404(TypeAttribute, pk=attributenumber)
                try:
                    attribute = TypeAttributeValue.objects.filter(device = device.pk).get(typeattribute=attributenumber)
                except:
                    attribute = TypeAttributeValue()
                    attribute.device = device
                    attribute.typeattribute = typeattribute
                attribute.value = value
                attribute.save()
            elif key.startswith("attribute_") and value == "":
                attributenumber = key.split("_")[1]
                try:
                    TypeAttributeValue.objects.filter(device = device.pk).get(typeattribute=attributenumber).delete()
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
            template.send(request=self.request, recipients=recipients, data={"device":device, "user":self.request.user})

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
            (reverse("device-detail", kwargs={"pk":context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context

class DeviceLend(FormView):
    template_name = 'devices/base_form.html'
    form_class = LendForm

    def get_context_data(self, **kwargs):
        context = super(DeviceLend, self).get_context_data(**kwargs)
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Mark device as lend"
        context['form_scripts'] = "$('#id_owner').select2();"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":device.pk}), device.name),
            ("", _("Lend"))]
        return context

    def form_valid(self, form):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(self.request, _("Archived Devices can't be lendt"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
        lending = Lending()
        lending.owner = get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)
        lending.duedate = form.cleaned_data["duedate"]
        lending.device = device
        lending.save()
        device.currentlending = lending
        if form.cleaned_data["room"]:
            device.room = form.cleaned_data["room"]
            reversion.set_comment(_("Device lendt and moved to room {0}").format(device.room))
        device.save()
        reversion.set_ignore_duplicates(True)
        messages.success(self.request, _('Device is marked as lendt to {0}').format(get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceInventoried(View):

    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        device.inventoried = datetime.datetime.now()
        device.save()
        reversion.set_ignore_duplicates(True)
        messages.success(request, _('Device is marked as inventoried.'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

    def post(self, request, **kwargs):
        return self.get(request, **kwargs)

class DeviceReturn(View):

    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(request, _("Archived Devices can't be returned"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
        lending = device.currentlending
        lending.returndate = datetime.datetime.utcnow().replace(tzinfo=utc)
        lending.save()
        device.currentlending = None
        device.save()
        reversion.set_ignore_duplicates(True)
        messages.success(request, _('Device is marked as returned.'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

    def post(self, request, **kwargs):
        return self.get(request, **kwargs)

class DeviceMail(FormView):
    template_name = 'devices/base_form.html'
    form_class = DeviceMailForm

    def get_context_data(self, **kwargs):
        context = super(DeviceMail, self).get_context_data(**kwargs)
        
        # Add in a QuerySet of all the books
        context['form_scripts'] = "$('#id_owner').select2();"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":self.device.pk}), self.device.name),
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
        template.send(self.request, recipients, {"device":device, "user":self.request.user})
        if template.usage == "reminder" or template.usage == "overdue":
            device.currentlending.duedate_email = datetime.datetime.utcnow().replace(tzinfo=utc)
            device.currentlending.save()
        messages.success(self.request, _('Mail successfully sent'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

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
        messages.success(request, _("Device was archived."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceTrash(SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Device
    template_name = 'devices/device_archive.html'

    def post(self, request, **kwargs):
        device = self.get_object()
        if device.trashed == None:
            device.trashed = datetime.datetime.utcnow().replace(tzinfo=utc)
            device.room = None
            device.currentlending = None
            for ip in device.ipaddress_set.all():
                ip.device = None
                ip.save()
        else:
            device.trashed = None
        device.save()
        #reversion.set_comment("Archived")
        reversion.set_ignore_duplicates(True)
        messages.success(request, _("Device was trashed."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))


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
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class TemplateList(PaginationMixin, ListView):
    model = Template
    context_object_name = 'template_list'
    
    def get_context_data(self, **kwargs):
        context = super(TemplateList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("template-list"), _("Templates")),]

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
        context["viewform"] = ViewForm(initial={"viewsorting":self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring":self.filterstring})
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
        context["merge_list"] = Room.objects.exclude(pk=context["room"].pk).order_by("name").values("id", "name", "building__name")
        context['device_list'] = Device.objects.select_related().filter(room=context["room"], archived=None).values("id", "name", "inventorynumber", "devicetype__name")

        if "room" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["room"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(context["room"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(context["room"], attribute))

        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk":context["room"].pk}), context["room"].name)]
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
            (reverse("room-detail", kwargs={"pk":context["object"].pk}), context["object"].name),
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
            (reverse("room-detail", kwargs={"pk":context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context

class RoomMerge(View):
    model = Room

    def get(self,  request, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk":context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    @commit_on_success
    def post(self,  request, **kwargs):
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
        context["viewform"] = ViewForm(initial={"viewsorting":self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring":self.filterstring})
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
        context['device_list'] = Device.objects.select_related().filter(room__building=context["building"], archived=None)

        if "building" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["building"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(context["building"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(context["building"], attribute))

        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk":context["building"].pk}), context["building"].name)]
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
            (reverse("building-detail", kwargs={"pk":context["object"].pk}), context["object"].name),
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
            (reverse("building-detail", kwargs={"pk":context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context

class BuildingMerge(View):
    model = Building

    def get(self,  request, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk":context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    @commit_on_success
    def post(self,  request, **kwargs):
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
        context["viewform"] = ViewForm(initial={"viewsorting":self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring":self.filterstring})
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
        context['device_list'] = Device.objects.filter(manufacturer=context["object"], archived=None)

        if "manufacturer" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["manufacturer"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(context["manufacturer"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(context["manufacturer"], attribute))

        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            (reverse("manufacturer-detail", kwargs={"pk":context["object"].pk}), context["object"].name)]
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
            (reverse("manufacturer-detail", kwargs={"pk":context["object"].pk}), context["object"].name),
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
            (reverse("manufacturer-detail", kwargs={"pk":context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context

class ManufacturerMerge(View):
    model = Manufacturer

    def get(self,  request, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        context["breadcrumbs"] = [
            (reverse("manufacturer-list"), _("Manufacturers")),
            (reverse("manufacturer-detail", kwargs={"pk":context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    @commit_on_success
    def post(self,  request, **kwargs):
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
            (reverse("device-detail", kwargs={"pk":device.pk}), device),
            ("", _("Notes")),
            ("", _("Create new note"))]
        return context

class NoteUpdate(UpdateView):
    model = Note
    template_name = 'devices/base_form.html'

    def get_success_url(self):
        return reverse_lazy("device-detail", kwargs={"pk":self.object.device.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NoteUpdate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":context["object"].device.pk}), context["object"].device.name),
            ("", _("Edit"))]
        return context

class NoteDelete(DeleteView):
    model = Note
    template_name = 'devices/base_delete.html'

    def get_success_url(self):
        return reverse_lazy("device-detail", kwargs={"pk":self.object.device.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NoteDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":context["object"].device.pk}), context["object"].device.name),
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
                isIP = True
                for element in item.split("."):
                    try:
                        intelement = int(element)
                        if not (intelement >= 0 and intelement <= 255):
                            isIP = False
                    except:
                        isIP = False
                if isIP:
                    searchlist[i] = "ipaddress: " + item
            elif len(item) == 7:
                try:
                    int(item)
                    searchlist[i] = "id: " + item
                except:
                    pass
        context["searchterm"] = " ".join(searchlist)

        return render_to_response(self.template_name, context, RequestContext(self.request))