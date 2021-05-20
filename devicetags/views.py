from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView

from devices.forms import VIEWSORTING
from devices.forms import FilterForm
from devices.forms import ViewForm
from devices.models import Device
from devicetags.forms import DeviceTagForm
from devicetags.forms import TagForm
from devicetags.models import Devicetag
from Lagerregal.utils import PaginationMixin
from users.mixins import PermissionRequiredMixin


class DevicetagList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Devicetag
    context_object_name = 'devicetag_list'
    permission_required = 'devicetags.view_devicetag'

    def get_queryset(self):
        devicetags = Devicetag.objects.all()

        # filtering devicetags
        self.filterstring = self.request.GET.get("filter", None)
        if self.filterstring:
            devicetags = devicetags.filter(name__icontains=self.filterstring)

        # sort view of devicetags by name or ID
        self.viewsorting = self.request.GET.get("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devicetags = devicetags.order_by(self.viewsorting)

        return devicetags

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetags"))]
        context["viewform"] = ViewForm(initial={"sorting": self.viewsorting})

        # filtering
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filter": self.filterstring})
        else:
            context["filterform"] = FilterForm()

        # add page number to breadcrumbs
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])

        return context


class DevicetagCreate(PermissionRequiredMixin, CreateView):
    model = Devicetag
    success_url = reverse_lazy('devicetag-list')
    template_name = 'devices/base_form.html'
    form_class = TagForm
    permission_required = 'devicetags.add_devicetag'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['type'] = "devicetag"

        # add "create new devicetag" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetag")),
            ("", _("Create new devicetag"))]

        return context


class DevicetagUpdate(PermissionRequiredMixin, UpdateView):
    model = Devicetag
    success_url = reverse_lazy('devicetag-list')
    template_name = 'devices/base_form.html'
    form_class = TagForm
    permission_required = 'devicetags.change_devicetag'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # adds "Devicetag" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetag")),
            (reverse("devicetag-edit", kwargs={"pk": self.object.pk}), self.object)]

        return context


class DevicetagDelete(PermissionRequiredMixin, DeleteView):
    model = Devicetag
    success_url = reverse_lazy('devicetag-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'devicetags.delete_devicetag'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # adds "Devicetag" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicetag-list"), _("Devicetags")),
            (reverse("devicetag-delete", kwargs={"pk": self.object.pk}), self.object)]

        return context


class DeviceTags(FormView):
    template_name = 'devices/base_form.html'
    form_class = DeviceTagForm
    success_url = "/devices"

    def dispatch(self, request, **kwargs):
        self.object = get_object_or_404(Device, pk=self.kwargs['pk'])
        return super().dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # adds "Devices" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("device-list"), _("Devices")),
            (reverse("device-detail", kwargs={"pk": self.object.pk}), self.object.name),
            ("", _("Assign Tags"))]

        return context

    def form_valid(self, form):
        tags = form.cleaned_data["tags"]
        self.object.tags.add(*tags)

        return HttpResponseRedirect(reverse("device-detail", kwargs={"pk": self.object.pk}))


class DeviceTagRemove(PermissionRequiredMixin, DeleteView):
    template_name = 'devicetags/remove_tag.html'
    model = Devicetag
    permission_required = 'devicetags.delete_devicetag'

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
