from django.conf import settings
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import View

from reversion import revisions as reversion

from devices.forms import VIEWSORTING
from devices.forms import FilterForm
from devices.forms import ViewForm
from devices.models import Device
from Lagerregal.utils import PaginationMixin
from locations.models import Building
from locations.models import Room
from locations.models import Section
from users.mixins import PermissionRequiredMixin


class SectionList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Section
    context_object_name = 'section_list'
    permission_required = 'locations.view_section'

    def get_queryset(self):
        sections = Section.objects.all()
        self.filterstring = self.request.GET.get("filter", None)
        if self.filterstring:
            sections = sections.filter(name__icontains=self.filterstring)
        self.viewsorting = self.request.GET.get("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            sections = sections.order_by(self.viewsorting)
        return sections

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections"))]
        context["viewform"] = ViewForm(initial={"sorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filter": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class SectionCreate(PermissionRequiredMixin, CreateView):
    model = Section
    success_url = reverse_lazy('section-list')
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'locations.add_section'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['type'] = "section"
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Section")),
            ("", _("Create new section"))]
        return context


class SectionDetail(PermissionRequiredMixin, DetailView):
    model = Section
    context_object_name = 'section'
    template_name = "locations/section_detail.html"
    permission_required = 'locations.view_section'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Section.objects.exclude(pk=context["object"].pk).order_by("name")
        context['device_list'] = Device.objects.filter(room__section=context["object"], archived=None,
                                                       trashed=None).values("id", "name", "inventorynumber",
                                                                            "devicetype__name")

        if "section" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["section"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(
                        context["section"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(
                        context["section"], attribute))
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections")),
            (reverse("section-detail", kwargs={"pk": context["object"].pk}), context["object"].name)]
        return context


class SectionUpdate(PermissionRequiredMixin, UpdateView):
    model = Section
    success_url = reverse_lazy('section-list')
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'locations.change_section'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Section")),
            (reverse("section-edit", kwargs={"pk": self.object.pk}), self.object)]
        return context


class SectionDelete(PermissionRequiredMixin, DeleteView):
    model = Section
    success_url = reverse_lazy('section-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'locations.delete_section'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections")),
            (reverse("section-delete", kwargs={"pk": self.object.pk}), self.object)]
        return context


class SectionMerge(PermissionRequiredMixin, View):
    model = Section
    permission_required = 'locations.change_section'

    def get(self, request, *args, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections")),
            (reverse("section-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render(request, 'devices/base_merge.html', context)

    @atomic
    def post(self, request, *args, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        rooms = Room.objects.filter(section=oldobject)
        for room in rooms:
            room.section = newobject
            reversion.set_comment(_("Merged Section {0} into {1}".format(oldobject, newobject)))
            room.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())


class RoomList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Room
    context_object_name = 'room_list'
    permission_required = 'devices.view_room'

    def get_queryset(self):
        rooms = Room.objects.select_related("building").all()
        self.filterstring = self.request.GET.get("filter", None)
        if self.filterstring:
            rooms = rooms.filter(name__icontains=self.filterstring)
        self.viewsorting = self.request.GET.get("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            rooms = rooms.order_by(self.viewsorting)
        return rooms

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("room-list"), _("Rooms"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filter": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class RoomDetail(PermissionRequiredMixin, DetailView):
    model = Room
    context_object_name = 'room'
    permission_required = 'devices.view_room'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
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


class RoomCreate(PermissionRequiredMixin, CreateView):
    model = Room
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devices.add_room'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Room"
        context['type'] = "room"
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            ("", _("Create new room"))]
        return context


class RoomUpdate(PermissionRequiredMixin, UpdateView):
    model = Room
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devices.change_room'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Edit"))]
        return context


class RoomDelete(PermissionRequiredMixin, DeleteView):
    model = Room
    success_url = reverse_lazy('room-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'devices.delete_room'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("room-list"), _("Rooms")),
            (reverse("room-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context


class RoomMerge(PermissionRequiredMixin, View):
    model = Room
    permission_required = 'devices.change_room'

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


class BuildingList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Building
    context_object_name = 'building_list'
    permission_required = 'devices.view_building'

    def get_queryset(self):
        buildings = Building.objects.all()
        self.filterstring = self.request.GET.get("filter", None)
        if self.filterstring:
            buildings = buildings.filter(name__icontains=self.filterstring)
        self.viewsorting = self.request.GET.get("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            buildings = buildings.order_by(self.viewsorting)
        return buildings

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("building-list"), _("Buildings"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filter": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        return context


class BuildingDetail(PermissionRequiredMixin, DetailView):
    model = Building
    context_object_name = 'building'
    permission_required = 'devices.view_building'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
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


class BuildingCreate(PermissionRequiredMixin, CreateView):
    model = Building
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devices.add_building'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Building"
        context['type'] = "building"
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            ("", _("Create new building"))]
        return context


class BuildingUpdate(PermissionRequiredMixin, UpdateView):
    model = Building
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devices.change_building'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Edit"))]
        return context


class BuildingDelete(PermissionRequiredMixin, DeleteView):
    model = Building
    success_url = reverse_lazy('building-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'devices.delete_building'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("building-list"), _("Buildings")),
            (reverse("building-detail", kwargs={"pk": context["object"].pk}), context["object"].name),
            ("", _("Delete"))]
        return context


class BuildingMerge(PermissionRequiredMixin, View):
    model = Building
    permission_required = 'devices.change_building'

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
