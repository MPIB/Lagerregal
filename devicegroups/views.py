from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from devicegroups.models import Devicegroup
from devices.models import Device
from django.utils.translation import ugettext_lazy as _
from devices.forms import ViewForm, VIEWSORTING

class DevicegroupList(ListView):
    model = Devicegroup
    context_object_name = 'devicegroup_list'
    
    def get_queryset(self):
        devicegroups = Devicegroup.objects.all()
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devicegroups = devicegroups.order_by(self.viewsorting)
        return devicegroups


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicegroupList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups"))]
        context["viewform"] = ViewForm(initial={"viewsorting":self.viewsorting})
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class DevicegroupDetail(DetailView):
    model = Devicegroup
    context_object_name = 'devicegroup'
    template_name = "devicegroups/devicegroup_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DevicegroupDetail, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            (reverse("devicegroup-detail", kwargs={"pk":self.object.pk}), self.object)]
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
            (reverse("devicegroup-detail", kwargs={"pk":self.object.pk}), self.object),
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
            (reverse("devicegroup-detail", kwargs={"pk":self.object.pk}), self.object),
            ("", _("Delete"))]
        return context