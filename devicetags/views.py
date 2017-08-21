from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from devicetags.models import Devicetag
from devices.models import Device
from devices.forms import ViewForm, VIEWSORTING, FilterForm
from devicetags.forms import TagForm, DeviceTagForm
from Lagerregal.utils import PaginationMixin


class DevicetagList(PaginationMixin, ListView):
    model = Devicetag
    context_object_name = 'devicetag_list'

    def get_queryset(self):
        devicetags = Devicetag.objects.all()

        # filtering devicetags
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            devicetags = devicetags.filter(name__icontains=self.filterstring)

        # sort view of devicetags by name or ID
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devicetags = devicetags.order_by(self.viewsorting)

        return devicetags


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicetagList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetags"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})

        # filtering
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()

        # add page number to breadcrumbs
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])

        return context


class DevicetagCreate(CreateView):
    model = Devicetag
    success_url = reverse_lazy('devicetag-list')
    template_name = 'devices/base_form.html'
    form_class = TagForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicetagCreate, self).get_context_data(**kwargs)
        context['type'] = "devicetag"

        # add "create new devicetag" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetag")),
            ("", _("Create new devicetag"))]

        return context


class DevicetagUpdate(UpdateView):
    model = Devicetag
    success_url = reverse_lazy('devicetag-list')
    template_name = 'devices/base_form.html'
    form_class = TagForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicetagUpdate, self).get_context_data(**kwargs)

        # adds "Devicetag" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetag")),
            (reverse("devicetag-edit", kwargs={"pk": self.object.pk}), self.object)]

        return context


class DevicetagDelete(DeleteView):
    model = Devicetag
    success_url = reverse_lazy('devicetag-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicetagDelete, self).get_context_data(**kwargs)

        # adds "Devicetag" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetags")),
            (reverse("devicetag-delete", kwargs={"pk": self.object.pk}), self.object)]

        return context


class DeviceTags(FormView):
    template_name = 'devices/base_form.html'
    form_class = DeviceTagForm
    success_url = "/devices"

    def get_context_data(self, **kwargs):
        context = super(DeviceTags, self).get_context_data(**kwargs)
        device = context["form"].cleaned_data["device"]

        # adds "Devices" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": device.pk}), device.name),
            ("", _("Assign Tags"))]

        return context

    def form_valid(self, form):
        tags = form.cleaned_data["tags"]
        device = form.cleaned_data["device"]
        device.tags.add(*tags)

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))


class DeviceTagRemove(DeleteView):
    template_name = 'devicetags/remove_tag.html'
    model = Devicetag

    def get(self, request, *args, **kwargs):
        context = {}
        context["device"] = get_object_or_404(Device, pk=kwargs["pk"])
        context["tag"] = get_object_or_404(Devicetag, pk=kwargs["tag"])

        # adds "Devices" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": context["device"].pk}), context["device"].name),
            ("", _("Remove Tag"))]

        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        device = get_object_or_404(Device, pk=kwargs["pk"])
        tag = get_object_or_404(Devicetag, pk=kwargs["tag"])
        tag.devices.remove(device.pk)
        tag.save()

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": device.pk}))
