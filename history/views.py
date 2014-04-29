from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, FormView, TemplateView
from Lagerregal.utils import PaginationMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from devices.models import Device, Template, Room, Building, Manufacturer, Lending, Note, Bookmark
from django.contrib.contenttypes.models import ContentType
from devicetypes.models import Type, TypeAttribute, TypeAttributeValue
from django.shortcuts import render_to_response
from django.template import RequestContext
from reversion.models import Version, Revision
# Create your views here.
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
        return render_to_response('history/device_history.html', context, RequestContext(request))

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
    template_name = 'history/device_history_list.html'

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

class Globalhistory(PaginationMixin, ListView):
    queryset = Revision.objects.select_related("version_set", "version_set__content_type", "user"
    	).filter().order_by("-date_created")
    context_object_name = "revision_list"
    template_name = 'history/globalhistory.html'

    def get_context_data(self, **kwargs):
        context = super(Globalhistory, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("globalhistory"), _("Global edit history"))]
        if context["is_paginated"]  and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class HistoryDetail(View):
    def get(self, request, **kwargs):
        versionid = kwargs["version"]
        current_version = get_object_or_404(Device, pk=kwargs["pk"])
        this_version = get_object_or_404(Version, pk=versionid)

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
        return render_to_response('history/device_history.html', context, RequestContext(request))
