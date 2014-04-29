from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from devicegroups.models import Devicegroup
from devices.models import Device
from devices.forms import ViewForm, VIEWSORTING, FilterForm
from Lagerregal.utils import PaginationMixin


class DevicegroupList(PaginationMixin, ListView):
    model = Devicegroup
    context_object_name = 'devicegroup_list'

    def get_queryset(self):
        devicegroups = Devicegroup.objects.all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            devicegroups = devicegroups.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devicegroups = devicegroups.order_by(self.viewsorting)
        return devicegroups


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicegroupList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class DevicegroupDetail(DetailView):
    model = Devicegroup
    context_object_name = 'devicegroup'
    template_name = "devicegroups/devicegroup_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicegroupDetail, self).get_context_data(**kwargs)

        if "devicegroup" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["devicegroup"][1]:
                context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(
                    context["devicegroup"], attribute))

        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            (reverse("devicegroup-detail", kwargs={"pk": self.object.pk}), self.object)]
        context['device_list'] = Device.objects.filter(group=context["devicegroup"], archived=None)
        return context


class DevicegroupCreate(CreateView):
    model = Devicegroup
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicegroupCreate, self).get_context_data(**kwargs)
        context['type'] = "devicegroup"
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            ("", _("Create new devicegroup"))]
        return context


class DevicegroupUpdate(UpdateView):
    model = Devicegroup
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicegroupUpdate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            (reverse("devicegroup-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Edit"))]
        return context


class DevicegroupDelete(DeleteView):
    model = Devicegroup
    success_url = reverse_lazy('devicegroup-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicegroupDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            (reverse("devicegroup-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Delete"))]
        return context