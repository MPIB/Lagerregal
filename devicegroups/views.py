from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from devicegroups.models import Devicegroup
from devices.forms import VIEWSORTING
from devices.forms import DepartmentViewForm
from devices.forms import FilterForm
from devices.models import Device
from Lagerregal.utils import PaginationMixin
from users.mixins import PermissionRequiredMixin
from users.models import Department


class DevicegroupList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Devicegroup
    context_object_name = 'devicegroup_list'
    permission_required = 'devicegroups.view_devicegroup'

    def get_queryset(self):
        '''method to query all devicegroups and filter and sort it'''
        devicegroups = Devicegroup.objects.all()
        self.filterstring = self.request.GET.get("filter", None)

        # if there is a filterstring, select the matching results
        if self.filterstring == "None":
            self.filterstring = None
        if self.filterstring:
            devicegroups = devicegroups.filter(name__icontains=self.filterstring)

        # sort list of devices by name or ID
        self.viewsorting = self.request.GET.get("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devicegroups = devicegroups.order_by(self.viewsorting)

        if self.request.user.departments.count() > 0:
            self.departmentfilter = self.request.GET.get("department", "my")
        else:
            self.departmentfilter = self.request.GET.get("department", "all")

        if self.departmentfilter != "all" and self.departmentfilter != "my":
            try:
                departmentid = int(self.departmentfilter)
                self.departmentfilter = Department.objects.get(id=departmentid)
            except:
                self.departmentfilter = Department.objects.get(name=self.departmentfilter)

            devicegroups = devicegroups.filter(Q(department=self.departmentfilter) | Q(department=None))
            self.departmentfilter = self.departmentfilter.id

        elif self.departmentfilter == "my":
            departmentfilter = self.request.user.departments.all()
            devicegroups = devicegroups.filter(Q(department__in=departmentfilter) | Q(department=None))

        return devicegroups

    def get_context_data(self, **kwargs):
        '''method for getting context data and use it'''
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups"))
        ]
        context["viewform"] = DepartmentViewForm(initial={
            "sorting": self.viewsorting,
            "department": self.departmentfilter,
        })

        # filtering
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filter": self.filterstring})
        else:
            context["filterform"] = FilterForm()

        # show page number in breadcrumbs
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])

        return context


class DevicegroupDetail(PermissionRequiredMixin, DetailView):
    model = Devicegroup
    context_object_name = 'devicegroup'
    template_name = "devicegroups/devicegroup_detail.html"
    permission_required = 'devicegroups.view_devicegroup'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # if label templates exist, use it to show details
        if "devicegroup" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["devicegroup"][1]:
                context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(
                    context["devicegroup"], attribute))

        # add devicegroup to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            (reverse("devicegroup-detail", kwargs={"pk": self.object.pk}), self.object)]
        context['device_list'] = Device.objects.filter(group=context["devicegroup"], archived=None)

        return context


class DevicegroupCreate(PermissionRequiredMixin, CreateView):
    model = Devicegroup
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devicegroups.add_devicegroup'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['type'] = "devicegroup"

        # if user has main department use it as default in form
        if self.request.user.main_department:
            context["form"].fields["department"].initial = self.request.user.main_department

        # add "create new device" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            ("", _("Create new devicegroup"))]

        return context


class DevicegroupUpdate(PermissionRequiredMixin, UpdateView):
    model = Devicegroup
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devicegroups.change_devicegroup'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # add devicegroup and "edit" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            (reverse("devicegroup-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Edit"))]

        return context


class DevicegroupDelete(PermissionRequiredMixin, DeleteView):
    model = Devicegroup
    success_url = reverse_lazy('devicegroup-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'devicegroups.delete_devicegroup'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # should add devicegroup and "delete" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("devicegroup-list"), _("Devicegroups")),
            (reverse("devicegroup-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Delete"))]

        return context
