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
from devices.models import Room
from Lagerregal.utils import PaginationMixin
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
