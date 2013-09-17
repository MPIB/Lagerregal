from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy, reverse
from devices.models import Device, Template, Room, Building, Manufacturer, Lending
from devicetypes.models import Type, TypeAttribute, TypeAttributeValue
from network.models import IpAddress
from mail.models import MailTemplate
from django.shortcuts import render_to_response
from reversion.models import Version
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.formats import localize
from django.contrib import messages
from devices.forms import IpAddressForm, SearchForm, LendForm, ViewForm, DeviceForm, DeviceMailForm
import datetime
import reversion
from django.contrib.auth.models import Permission
from users.models import Lageruser
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

class DeviceList(ListView):
    context_object_name = 'device_list'

    def get_queryset(self):
        self.viewfilter = self.kwargs.pop("filter", "active")
        if self.viewfilter == "all":
            return Device.objects.all()
        elif self.viewfilter == "available":
            return Device.objects.filter(currentlending=None)
        elif self.viewfilter == "unavailable":
            return Device.objects.exclude(currentlending=None)
        elif self.viewfilter == "archived":
            return Device.objects.exclude(archived=None)
        else:
            return Device.objects.filter(archived=None)

    def get_context_data(self, **kwargs):
        context = super(DeviceList, self).get_context_data(**kwargs)
        context["viewform"] = ViewForm(initial={'viewfilter': self.viewfilter})
        context["template_list"] = Template.objects.all()
        context["breadcrumbs"] = [[reverse("device-list"), _("Devices")]]
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class DeviceDetail(DetailView):
    model = Device
    context_object_name = 'device'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['ipaddress_list'] = IpAddress.objects.filter(device=context['device'])
        context['ipaddress_available'] = IpAddress.objects.filter(device=None)
        context['ipaddressform'] = IpAddressForm()
        context["lending_list"] = Lending.objects.filter(device=context["device"]).order_by("-pk")
        context["today"] = datetime.date.today()
        context["weekago"] = context["today"] - datetime.timedelta(days=7)
        context["attributevalue_list"] = TypeAttributeValue.objects.filter(device=context["device"])
        context["lendform"] = LendForm()
        
        mailinitial = {}
        if context["device"].currentlending != None:
            mailinitial["recipient"] = context["device"].currentlending.owner
        try:
            mailinitial["mailtemplate"] = MailTemplate.objects.get(usage="reminder")
        except:
            pass
        context["mailform"] = DeviceMailForm(initial=mailinitial)

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
            ("", _("Version {}".format(this_version.revision.pk)))
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
            deleted_keys.append(_("Devicetype"))

        try:
            manufacturer = device.manufacturer
        except Manufacturer.DoesNotExist:
            device.manufacturer = None
            deleted_keys.append(_("Manufacturer"))

        try:
            room = device.room
        except Room.DoesNotExist:
            device.room = None
            deleted_keys.append(_("Room"))

        device.save()
        if version.field_dict["devicetype"] != None:        
            TypeAttributeValue.objects.filter(device = version.object_id).delete()
        reversion.set_comment("Reverted to version from {}".format(localize(version.revision.date_created)))
        reversion.set_ignore_duplicates(True)

        if deleted_keys == []:
            messages.success(self.request, _('Successfully reverted Device to revision {0}').format(version.revision.id))
        else:
            print "test"
            messages.warning(self.request, _("Reverted Device to revision {0}, but the following fields had to be set to null, as the referenced object was deleted: {1}").format(version.revision.id, ",".join(deleted_keys)))

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceHistoryList(View):

    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        version_list = Version.objects.filter(object_id=device.id, content_type_id=ContentType.objects.get(model='device').id).order_by("-pk")
        context = {"version_list":version_list, "device":device}
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":context["device"].pk}), context["device"].name),
            ("", _("History"))]
        return render_to_response('devices/device_history_list.html', context, RequestContext(request))


class DeviceCreate(CreateView):
    model = Device
    template_name = 'devices/device_form.html'
    form_class = DeviceForm

    def get_initial(self):
        super(DeviceCreate, self).get_initial()
        creator = self.request.user.pk
        templateid = self.kwargs.pop("templateid", None)
        if templateid != None:
            templatedict = get_object_or_404(Template, pk=templateid).get_as_dict()
            templatedict["creator"] = creator
            return templatedict
        copyid = self.kwargs.pop("copyid", None)
        if copyid != None:
            copydict = get_object_or_404(Device, pk=copyid).get_as_dict()
            copydict["creator"] = creator
            copydict["deviceid"] = copyid
            return copydict
        return {"creator":creator}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Device"
        context['form'].fields['emailbosses'].label = "Notify bosses about new device"
        context['form'].fields['emailmanagment'].label = "Notify managment about new device"
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
        
        if form.cleaned_data["emailbosses"] or form.cleaned_data["emailmanagment"]:
            if form.cleaned_data["emailbosses"]:
                perm = Permission.objects.get(codename='boss_mails')
                bosses = Lageruser.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()
                recipients = []
                for boss in bosses:
                    recipients.append(boss.email)
                template = form.cleaned_data["emailtemplatebosses"]
                template.send(recipients=recipients, data={"device":self.object})
            if form.cleaned_data["emailmanagment"]:
                perm = Permission.objects.get(codename='managment_mails')
                managment = Lageruser.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()
                recipients = []
                for m in managment:
                    recipients.append(m.email)
                template = form.cleaned_data["emailtemplatemanagment"]
                template.send(recipients=recipients, data={"device":self.object})

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
            if form.cleaned_data["devicetype"] == None:
                TypeAttributeValue.objects.filter(device = device.pk).delete()
            if device.devicetype.pk != form.cleaned_data["devicetype"].pk:
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

        if form.cleaned_data["emailbosses"] or form.cleaned_data["emailmanagment"]:
            if form.cleaned_data["emailbosses"]:
                perm = Permission.objects.get(codename='boss_mails')
                bosses = Lageruser.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()
                recipients = []
                for boss in bosses:
                    recipients.append(boss.email)
                template = form.cleaned_data["emailtemplatebosses"]
                template.send(recipients=recipients, data={"device":device})
            if form.cleaned_data["emailmanagment"]:
                perm = Permission.objects.get(codename='managment_mails')
                managment = Lageruser.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()
                recipients = []
                for m in managment:
                    recipients.append(m.email)
                template = form.cleaned_data["emailtemplatemanagment"]
                template.send(recipients=recipients, data={"device":device})

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
        device.save()
        reversion.set_ignore_duplicates(True)
        messages.success(self.request, _('Device is marked as lendt to {{0}}').format(get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceReturn(View):

    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(request, _("Archived Devices can't be returned"))
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
        lending = device.currentlending
        lending.returndate = datetime.datetime.now()
        lending.save()
        device.currentlending = None
        device.save()
        reversion.set_ignore_duplicates(True)
        messages.success(request, _('Device is marked as returned.'))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceMail(FormView):
    template_name = 'devices/base_form.html'
    form_class = DeviceMailForm

    def get_context_data(self, **kwargs):
        context = super(DeviceLend, self).get_context_data(**kwargs)
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        # Add in a QuerySet of all the books
        context['form_scripts'] = "$('#id_owner').select2();"
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk":device.pk}), device.name),
            ("", _("Send Mail"))]
        return context

    def form_valid(self, form):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        template = form.cleaned_data["mailtemplate"]
        recipient = form.cleaned_data["recipient"]
        template.send([recipient.email,], {"device":device, "owner":recipient, "user":self.request.user})
        messages.success(self.request, _('Mail sent to {0}').format(recipient))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
class DeviceArchive(SingleObjectTemplateResponseMixin, BaseDetailView):
    model = Device
    template_name = 'devices/device_archive.html'

    def post(self, request, **kwargs):
        device = self.get_object()
        if device.archived == None:
            device.archived = datetime.datetime.now()
            device.room = None
            device.currentlending = None
        else:
            device.archived = None
        device.save()
        #reversion.set_comment("Archived")
        reversion.set_ignore_duplicates(True)
        messages.success(request, _("Device was archived."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))


class DeviceGlobalhistory(ListView):
    queryset = Version.objects.filter(content_type_id=ContentType.objects.get(model='device').id).order_by("-pk")
    context_object_name = "revision_list"
    template_name = 'devices/globalhistory.html'

    def get_context_data(self, **kwargs):
        context = super(DeviceGlobalhistory, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [("", _("Global edit history"))]
        if context["is_paginated"]  and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30



class TemplateList(ListView):
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

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

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
            ("", _("Edit: {}".format(self.object.templatename)))]
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
            ("", _("Delete: {}".format(self.object.templatename)))]
        return context






class RoomList(ListView):
    model = Room
    context_object_name = 'room_list'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("room-list"), _("Rooms"))]

        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class RoomDetail(DetailView):
    model = Room
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Room.objects.exclude(pk=context["room"].pk)
        context['device_list'] = Device.objects.filter(room=context["room"], archived=None)
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
            ("", _("Merge with {}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    def post(self,  request, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        devices = Device.objects.filter(room=oldobject)
        for device in devices:
            device.room = newobject
            device.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())


class BuildingList(ListView):
    model = Building
    context_object_name = 'building_list'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("building-list"), _("Buildings"))]
        return context
    
    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class BuildingDetail(DetailView):
    model = Building
    context_object_name = 'building'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Building.objects.exclude(pk=context["building"].pk)
        context['device_list'] = Device.objects.filter(room__building=context["building"], archived=None)
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
            ("", _("Merge with {}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    def post(self,  request, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        rooms = Room.objects.filter(building=oldobject)
        for room in rooms:
            room.building = newobject
            room.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())


class ManufacturerList(ListView):
    model = Manufacturer
    context_object_name = 'manufacturer_list'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("manufacturer-list"), _("Manufacturers"))]
        
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class ManufacturerDetail(DetailView):
    model = Manufacturer
    context_object_name = 'object'
    template_name = "devices/manufacturer_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Manufacturer.objects.exclude(pk=context["object"].pk)
        context['device_list'] = Device.objects.filter(manufacturer=context["object"], archived=None)
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
            ("", _("Merge with {}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    def post(self,  request, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        devices = Device.objects.filter(manufacturer=oldobject)
        for device in devices:
            device.manufacturer = newobject
            device.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())

class Search(FormView):
    template_name = 'devices/search.html'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Search, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [("", _("Search"))]
        return context

    def form_valid(self, form):
        search = {}
        if form.cleaned_data["searchname"] != "":
            search["name__" + form.cleaned_data["namemodifier"]] = form.cleaned_data["searchname"]

        if form.cleaned_data["lender"] != "":
            search["currentlending__owner__username__icontains"] = form.cleaned_data["lender"]

        if form.cleaned_data["bildnumber"] != "":
            search["bildnumber__" + form.cleaned_data["bildnumbermodifier"]] = form.cleaned_data["bildnumber"]

        if form.cleaned_data["serialnumber"] != "":
            search["serialnumber__" + form.cleaned_data["serialnumbermodifier"]] = form.cleaned_data["serialnumber"]

        if form.cleaned_data["macaddress"] != "":
            search["name__" + form.cleaned_data["macaddressmodifier"]] = form.cleaned_data["macaddress"]

        if form.cleaned_data["devicetype"].exists():
            search["devicetype__in"] = form.cleaned_data["devicetype"]

        if form.cleaned_data["manufacturer"].exists():
            search["manufacturer__in"] = form.cleaned_data["manufacturer"]

        if form.cleaned_data["room"].exists():
            search["room__in"] = form.cleaned_data["room"]



        if form.cleaned_data["overdue"] == "y":
            search["duedate__gt"] = datetime.datetime.now()
        elif form.cleaned_data["overdue"] == "n":
            search["duedate__lt"] = datetime.datetime.now()

        if search == {} and form.cleaned_data["ipaddress"] == "":
            devices = []
        else:

            devices = Device.objects.filter(**search)

            if form.cleaned_data["ipaddress"] != "":
                devices = devices.filter(ipaddress__address__icontains=form.cleaned_data["ipaddress"]).distinct()

            viewfilter = form.cleaned_data["viewfilter"]
            if viewfilter == "all":
                pass
            elif viewfilter == "available":
                devices = devices.filter(currentlending=None)
            elif viewfilter == "unavailable":
                devices = devices.exclude(currentlending=None)
            elif viewfilter == "archived":
                devices = devices.exclude(archived=None)
            else:
                devices = devices.filter(archived=None)

        context = {
        "device_list":devices,
        "form":form,
        "breadcrumbs":[["", _("Searchresult")]]
        }
        return render_to_response('devices/searchresult.html', context, RequestContext(self.request))
