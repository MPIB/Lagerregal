from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.core.urlresolvers import reverse_lazy, reverse
from locations.models import Section
from devices.models import Device, Room
from django.utils.translation import ugettext_lazy as _
from devices.forms import ViewForm, VIEWSORTING, FilterForm
from django.conf import settings
from Lagerregal.utils import PaginationMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.transaction import commit_on_success
import reversion

class SectionList(PaginationMixin, ListView):
    model = Section
    context_object_name = 'section_list'

    def get_queryset(self):
        sections = Section.objects.all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            sections = sections.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            sections = sections.order_by(self.viewsorting)
        return sections


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SectionList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections"))]
        context["viewform"] = ViewForm(initial={"viewsorting":self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring":self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

class SectionCreate(CreateView):
    model = Section
    success_url = reverse_lazy('section-list')
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SectionCreate, self).get_context_data(**kwargs)
        context['type'] = "section"
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Section")),
            ("", _("Create new section"))]
        return context


class SectionDetail(DetailView):
    model = Section
    context_object_name = 'section'
    template_name = "locations/section_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SectionDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Section.objects.exclude(pk=context["object"].pk).order_by("name")
        context['device_list'] = Device.objects.filter(room__section=context["object"], archived=None, trashed=None).values("id", "name", "inventorynumber", "devicetype__name")

        if "section" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["section"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(context["section"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(context["section"], attribute))
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections")),
            (reverse("section-detail", kwargs={"pk":context["object"].pk}), context["object"].name)]
        return context

class SectionUpdate(UpdateView):
    model = Section
    success_url = reverse_lazy('section-list')
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SectionUpdate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Section")),
            (reverse("section-edit", kwargs={"pk":self.object.pk}), self.object)]
        return context


class SectionDelete(DeleteView):
    model = Section
    success_url = reverse_lazy('section-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SectionDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections")),
            (reverse("section-delete", kwargs={"pk":self.object.pk}), self.object)]
        return context

class SectionMerge(View):
    model = Section

    def get(self,  request, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Sections")),
            (reverse("section-detail", kwargs={"pk":context["oldobject"].pk}), context["oldobject"].name),
            ("", _("Merge with {0}".format(context["newobject"].name)))]
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    @commit_on_success
    def post(self,  request, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        rooms = Room.objects.filter(section=oldobject)
        for room in rooms:
            room.section = newobject
            reversion.set_comment(_("Merged Section {0} into {1}".format(oldobject, newobject)))
            room.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())