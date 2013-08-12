from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View, FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from django.template import RequestContext, loader, Context
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy, reverse
from devices.models import Device, Template, Room, Building, Manufacturer, Lending
from devicetypes.models import Type, TypeAttribute, TypeAttributeValue
from network.models import IpAddress
from django.shortcuts import render_to_response
import rest_framework.reverse
from reversion.models import Version
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.formats import localize
from django.contrib import messages
from devices.forms import IpAddressForm, SearchForm, LendForm, ViewForm, DeviceForm
import datetime
import reversion
from django.contrib.auth.models import Permission
from django.core.mail import EmailMessage
from users.models import Lageruser
from django.utils.translation import ugettext_lazy as _


class DeviceList(ListView):
    context_object_name = 'device_list'
    paginate_by = 30

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
        return context

class DeviceDetail(DetailView):
    model = Device
    context_object_name = 'device'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['ipaddress_list'] = IpAddress.objects.filter(device=context['device'])
        context['ipaddress_available'] = IpAddress.objects.filter(device=None)
        context['version_list'] = reversion.get_unique_for_object(context["device"])
        context['ipaddressform'] = IpAddressForm()
        context["lending_list"] = Lending.objects.filter(device=context["device"])
        context["today"] = datetime.date.today()
        context["weekago"] = context["today"] - datetime.timedelta(days=7)
        context["attributevalue_list"] = TypeAttributeValue.objects.filter(device=context["device"])
        context["lendform"] = LendForm()
        return context

class DeviceIpAddressRemove(DeleteView):
    template_name = 'devices/unassign_ipaddress.html'
    model = IpAddress

    def get(self, request, *args, **kwargs):
        context = {}
        context["device"] = get_object_or_404(Device, pk=kwargs["pk"])
        context["ipaddress"] = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        return render_to_response(self.template_name, context, RequestContext(request))


    def post(self, **kwargs):
        device = get_object_or_404(Device, pk=kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        ipaddress.device = None
        ipaddress.save()

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))


class DeviceIpAddress(FormView):
    template_name = 'devices/assign_ipaddress.html'
    form_class = IpAddressForm
    success_url = "/devices"

    def form_valid(self, form):
        ipaddresses = form.cleaned_data["ipaddresses"]
        device = form.cleaned_data["device"]
        if device.archived != None:
            messages.error(self.request, "Archived Devices can't get new IP-Addresses")
            return HttpResponseRedirect(self.reverse("device-detail", kwargs={"pk":device.pk}))
        for ipaddress in ipaddresses:
            ipaddress.device = device
            ipaddress.save()
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceHistory(View):

    def get(self, request, **kwargs):
        revisionid = kwargs["revision"]
        device = get_object_or_404(Device, pk=kwargs["pk"])
        this_version = get_object_or_404(Version, pk=revisionid)
        try:
            previous_version = Version.objects.filter(object_id=device.pk, revision__date_created__lt=this_version.revision.date_created).order_by("-pk")[0].field_dict
            previous_version["devicetype"] = Type.objects.get(pk=previous_version["devicetype"])
            previous_version["manufacturer"] = Manufacturer.objects.get(pk=previous_version["manufacturer"])
            previous_version["room"] = Room.objects.get(pk=previous_version["room"])
        except:
            previous_version = None
        this_version.field_dict["devicetype"] = Type.objects.get(pk=this_version.field_dict["devicetype"])
        this_version.field_dict["manufacturer"] = Manufacturer.objects.get(pk=this_version.field_dict["manufacturer"])
        this_version.field_dict["room"] = Room.objects.get(pk=this_version.field_dict["room"])
        context = {"version":this_version, "previous":previous_version, "this_version":this_version.field_dict, "current":device}
        return render_to_response('devices/device_history.html', context, RequestContext(request))

    def post(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(self.request, "Archived Devices can't be reverted")
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
        revisionid = kwargs["revision"]

        version = get_object_or_404(Version, pk=revisionid)
        version.revision.revert()
        reversion.set_comment("Reverted to version from {}".format(localize(version.revision.date_created)))
        messages.success(self.request, 'Successfully reverted Device')
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceHistoryList(View):

    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        version_list = reversion.get_unique_for_object(device)
        context = {"version_list":version_list, "device":device}
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
            return copydict
        return {"creator":creator}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DeviceCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Device"
        context['form'].fields['emailbosses'].label = "Notify bosses about new device"
        context['form'].fields['emailmanagment'].label = "Notify managment about new device"
        return context

    def form_valid(self, form):
        if form.cleaned_data["emailbosses"] or form.cleaned_data["emailbosses"]:
            subject = "New device was added"

            c = Context({
                "name", form.cleaned_data["name"]
            })
            body = render_to_string("mails/newdevice.html", c)
            email = EmailMessage(subject=subject, body=body)
            if form.cleaned_data["emailbosses"]:
                bosses = Lageruser.objects.filter(
                    groups__permissions = Permission.objects.get(codename='boss_mail'))
                for boss in bosses:
                    email.to.append(boss.email)
            if form.cleaned_data["emailmanagment"]:
                managment = Lageruser.objects.filter(
                    groups__permissions = Permission.objects.get(codename='managment_mail'))
                for m in managment:
                    email.to.append(m.email)
            email.send()
        form.cleaned_data["creator"] = self.request.user
        reversion.set_comment("Created")
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
        return context

    def form_valid(self, form):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(self.request, "Archived Devices can't be edited")
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
        else:
            reversion.set_comment("Updated")
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
            messages.success(self.request, _('Device was successfully updated.'))
            return super(DeviceUpdate, self).form_valid(form)


class DeviceDelete(DeleteView):
    model = Device
    success_url = reverse_lazy('device-list')
    template_name = 'devices/base_delete.html'

class DeviceLend(FormView):
    template_name = 'devices/base_form.html'
    form_class = LendForm

    def get_context_data(self, **kwargs):
        context = super(DeviceLend, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Mark device as lend"
        context['form_scripts'] = "$('#id_owner').select2();"
        return context


    def form_valid(self, form):
        deviceid = self.kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(self.request, "Archived Devices can't be lendt")
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
        messages.success(self.request, _('Device is marked as lendt to {{0}}').format(get_object_or_404(Lageruser, pk=form.cleaned_data["owner"].pk)))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))



class DeviceReturn(View):

    def get(self, request, **kwargs):
        deviceid = kwargs["pk"]
        device = get_object_or_404(Device, pk=deviceid)
        if device.archived != None:
            messages.error(request, "Archived Devices can't be returned")
            return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))
        lending = device.currentlending
        lending.returndate = datetime.datetime.now()
        lending.save()
        device.currentlending = None
        device.save()
        messages.success(request, _('Device is marked as returned.'))
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
        reversion.set_comment("Archived")
        messages.success(request, _("Device was archived."))
        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))


class DeviceGlobalhistory(ListView):
    queryset = Version.objects.order_by('-pk')
    context_object_name = "revision_list"
    template_name = 'devices/globalhistory.html'
    paginate_by = 30

class TemplateList(ListView):
    model = Template
    context_object_name = 'template_list'
    paginate_by = 30

class TemplateCreate(CreateView):
    model = Template
    template_name = 'devices/base_form.html'

class TemplateUpdate(UpdateView):
    model = Template
    template_name = 'devices/base_form.html'

class TemplateDelete(DeleteView):
    model = Template
    success_url = reverse_lazy('device-list')
    template_name = 'devices/base_delete.html'






class RoomList(ListView):
    model = Room
    context_object_name = 'room_list'
    paginate_by = 30

class RoomDetail(DetailView):
    model = Room
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Room.objects.exclude(pk=context["room"].pk)
        context['device_list'] = Device.objects.filter(room=context["room"], archived=None)
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
        return context

class RoomUpdate(UpdateView):
    model = Room
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RoomUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        return context

class RoomDelete(DeleteView):
    model = Room
    success_url = reverse_lazy('room-list')
    template_name = 'devices/base_delete.html'

class RoomMerge(View):
    model = Room

    def get(self, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    def post(self, **kwargs):
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
    paginate_by = 30

class BuildingDetail(DetailView):
    model = Building
    context_object_name = 'building'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Building.objects.exclude(pk=context["building"].pk)
        context['device_list'] = Device.objects.filter(room__building=context["building"], archived=None)
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
        return context

class BuildingUpdate(UpdateView):
    model = Building
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BuildingUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        return context

class BuildingDelete(DeleteView):
    model = Building
    success_url = reverse_lazy('building-list')
    template_name = 'devices/base_delete.html'

class BuildingMerge(View):
    model = Building

    def get(self, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    def post(self, **kwargs):
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
    paginate_by = 30

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
        return context

class ManufacturerUpdate(UpdateView):
    model = Manufacturer
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ManufacturerUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        return context

class ManufacturerDelete(DeleteView):
    model = Manufacturer
    success_url = reverse_lazy('manufacturer-list')
    template_name = 'devices/base_delete.html'

class ManufacturerMerge(View):
    model = Manufacturer

    def get(self, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    def post(self, **kwargs):
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

        if form.cleaned_data["devicetype"] != None:
            search["devicetype"] = form.cleaned_data["devicetype"]

        if form.cleaned_data["manufacturer"] != None:
            search["manufacturer"] = form.cleaned_data["manufacturer"]

        if form.cleaned_data["room"] != None:
            search["room"] = form.cleaned_data["room"]



        if form.cleaned_data["overdue"] == "y":
            search["duedate__gt"] = datetime.datetime.now()
        elif form.cleaned_data["overdue"] == "n":
            search["duedate__lt"] = datetime.datetime.now()



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
        "form":form
        }
        return render_to_response('devices/searchresult.html', context, RequestContext(self.request))
