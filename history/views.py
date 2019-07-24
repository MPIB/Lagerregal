from django.apps import apps
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import UpdateView

from reversion import revisions as reversion
from reversion.models import Revision
from reversion.models import Version

from devices.models import Device
from devices.models import Manufacturer
from devices.models import Room
from devicetypes.models import Type
from devicetypes.models import TypeAttributeValue
from Lagerregal.utils import PaginationMixin
from users.mixins import PermissionRequiredMixin


class Globalhistory(PermissionRequiredMixin, PaginationMixin, ListView):
    queryset = Revision.objects\
        .select_related("user")\
        .prefetch_related("version_set", "version_set__content_type")\
        .order_by("-date_created")
    context_object_name = "revision_list"
    template_name = 'history/globalhistory.html'
    permission_required = 'devices.change_device'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("globalhistory"), _("Global edit history"))]
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


excluded_fields = ["currentlending", "created_at", "archived", "trashed", "inventoried", "bookmarks", "trashed",
                   "last_seen", "creator"]


def cleanup_fielddict(version):
    del version.field_dict["id"]
    if version.field_dict.get("devicetype") is not None:
        try:
            version.field_dict["devicetype"] = Type.objects.get(
                pk=version.field_dict["devicetype"])
        except Type.DoesNotExist:
            version.field_dict["devicetype"] = "[deleted]"
    if version.field_dict.get("manufacturer") is not None:
        try:
            version.field_dict["manufacturer"] = Manufacturer.objects.get(
                pk=version.field_dict["manufacturer"])
        except Manufacturer.DoesNotExist:
            version.field_dict["manufacturer"] = "[deleted]"
    if version.field_dict.get("room") is not None:
        try:
            version.field_dict["room"] = Room.objects.get(
                pk=version.field_dict["room"])
        except Room.DoesNotExist:
            version.field_dict["room"] = "[deleted]"

    if version.field_dict.get("device") is not None:
        try:
            version.field_dict["device"] = Device.objects.get(
                pk=version.field_dict["device"])
        except Device.DoesNotExist:
            version.field_dict["device"] = "[deleted]"

    for excluded_field in excluded_fields:
        if excluded_field in version.field_dict:
            del version.field_dict[excluded_field]

    return version


class HistoryDetail(PermissionRequiredMixin, UpdateView):
    model = Version
    template_name = 'history/history_detail.html'
    context_object_name = "this_version"
    fields = "__all__"
    permission_required = 'devices.change_device'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = apps.get_model(
            context["this_version"].content_type.app_label,
            context["this_version"].content_type.model,
        )
        context["current_version"] = get_object_or_404(
            model, id=context["this_version"].object_id
        )

        context["this_version"] = cleanup_fielddict(context["this_version"])

        previous_version = Version.objects.filter(object_id=context["current_version"].pk,
                                                  revision__date_created__lt=context["this_version"].revision.date_created,
                                                  content_type_id=context["this_version"].content_type.id).order_by(
            "-pk")
        if len(previous_version) == 0:
            context["previous_version"] = None
        else:
            context["previous_version"] = cleanup_fielddict(previous_version[0])

        next_version = Version.objects.filter(object_id=context["current_version"].pk,
                                              revision__date_created__gt=context["this_version"].revision.date_created,
                                              content_type_id=context["this_version"].content_type.id).order_by("pk")
        if len(next_version) == 0:
            context["next_version"] = None
        else:
            context["next_version"] = next_version[0]

        context["breadcrumbs"] = [
            (reverse("{0}-list".format(context["this_version"].content_type.model)),
                _(context["this_version"].content_type.name)),
            (context["current_version"].get_absolute_url(), str(context["current_version"])),
            (reverse("history-list", kwargs={"content_type_id": context["this_version"].content_type.id,
                                             "object_id": context["this_version"].object_id}), _("History")),
            ("", _("Version {0}".format(context["this_version"].pk)))
        ]

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        version = context["this_version"]
        object = context["current_version"]

        for name, value in version.field_dict.items():
            if value == "[deleted]":
                setattr(object, name, None)
            else:
                setattr(object, name, value)

        object.save()
        if version.field_dict.get("devicetype") is not None:
            TypeAttributeValue.objects.filter(device=version.object_id).delete()
        reversion.set_comment("Reverted to version from {0}".format(version.revision.date_created))

        messages.success(
            self.request,
            _('Successfully reverted Device to revision {0}').format(
                version.revision.id
            ),
        )

        return HttpResponseRedirect(object.get_absolute_url())


class HistoryList(PermissionRequiredMixin, ListView):
    context_object_name = 'version_list'
    template_name = 'history/history_list.html'
    permission_required = 'devices.change_device'

    def get_queryset(self):
        object_id = self.kwargs["object_id"]
        content_type_id = self.kwargs["content_type_id"]
        self.content_type = get_object_or_404(ContentType, id=content_type_id)
        self.object = get_object_or_404(apps.get_model(self.content_type.app_label, self.content_type.model), id=object_id)
        return Version.objects.filter(object_id=self.object.id,
                                      content_type_id=self.content_type.id).order_by("-pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("{0}-list".format(self.content_type.model)),
                _(self.content_type.name)),
            (self.object.get_absolute_url(), str(self.object)),
            (reverse("history-list", kwargs={"content_type_id": self.content_type.id,
                                             "object_id": self.object.id}), _("History"))
        ]
        return context
