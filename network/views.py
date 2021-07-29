from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView

from reversion import revisions as reversion

from devices.forms import FilterForm
from Lagerregal.utils import PaginationMixin
from network.forms import IpAddressForm
from network.forms import UserIpAddressForm
from network.forms import ViewForm
from network.models import IpAddress
from users.mixins import PermissionRequiredMixin
from users.models import Lageruser


class IpAddressList(PermissionRequiredMixin, PaginationMixin, ListView):
    context_object_name = 'ipaddress_list'
    permission_required = 'network.view_ipaddress'

    def get_queryset(self):
        self.viewfilter = self.request.GET.get("category", "all")
        self.filterstring = self.request.GET.get("filter", "")
        if self.viewfilter == "all":
            addresses = IpAddress.objects.all()
        elif self.viewfilter == "free":
            addresses = IpAddress.objects.filter(device=None, user=None)
        elif self.viewfilter == "used":
            addresses = IpAddress.objects.exclude(device=None, user=None)
        elif self.viewfilter == "byuser":
            addresses = IpAddress.objects.exclude(user=None).filter(device=None)
        elif self.viewfilter == "bydevice":
            addresses = IpAddress.objects.exclude(device=None).filter(user=None)
        else:
            addresses = IpAddress.objects.all()

        if self.request.user.departments.count() > 0:
            self.departmentfilter = self.request.GET.get("department", "my")
        else:
            self.departmentfilter = self.request.GET.get("department", "all")

        if self.departmentfilter != "all" and self.departmentfilter != "my":
            addresses = addresses.filter(department__id=self.departmentfilter)
        elif self.departmentfilter == "my":
            addresses = addresses.filter(department__in=self.request.user.departments.all())

        if self.filterstring != "":
            addresses = addresses.filter(address__icontains=self.filterstring)
        return addresses.values("id", "address", "device__pk", "device__name", "user__pk", "user__username",
                                "user__first_name", "user__last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["viewform"] = ViewForm(initial={
            'category': self.viewfilter,
            "department": self.departmentfilter,
        })
        context["filterform"] = FilterForm(initial={
            "filter": self.filterstring
        })
        context["breadcrumbs"] = [(reverse("device-list"), _("IP-Addresses"))]

        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class IpAddressDetail(PermissionRequiredMixin, DetailView):
    model = IpAddress
    context_object_name = 'ipaddress'
    permission_required = 'network.view_ipaddress'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "ipaddress" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["ipaddress"][1]:
                context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute,
                                                                                          getattr(context["ipaddress"],
                                                                                                  attribute))

        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            (reverse("ipaddress-detail", kwargs={"pk": self.object.pk}), self.object.address)]
        return context


class IpAddressCreate(PermissionRequiredMixin, CreateView):
    model = IpAddress
    form_class = IpAddressForm
    template_name = 'devices/base_form.html'
    permission_required = 'network.add_ipaddress'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actionstring'] = _("Create new IP-Address")
        context["form"].fields["department"].queryset = self.request.user.departments.all()
        if self.request.user.main_department:
            context["form"].fields["department"].initial = self.request.user.main_department
        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            ("", _("Create new IP-Address"))]
        return context

    def form_valid(self, form):
        form.instance.address = ".".join(
            [(x.lstrip("0") if x != "0" else x) for x in form.cleaned_data["address"].split(".")])
        return super().form_valid(form)


class IpAddressUpdate(PermissionRequiredMixin, UpdateView):
    model = IpAddress
    form_class = IpAddressForm
    template_name = 'devices/base_form.html'
    permission_required = 'network.change_ipaddress'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["form"].fields["department"].queryset = self.request.user.departments.all()
        context['actionstring'] = _("Update")
        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            (reverse("ipaddress-detail", kwargs={"pk": self.object.pk}), self.object.address),
            ("", _("Edit"))]
        return context

    def form_valid(self, form):
        form.instance.address = ".".join(
            [(x.lstrip("0") if x != "0" else x) for x in form.cleaned_data["address"].split(".")])
        return super().form_valid(form)


class IpAddressDelete(PermissionRequiredMixin, DeleteView):
    template_name = 'devices/base_delete.html'
    model = IpAddress
    success_url = reverse_lazy('ipaddress-list')
    permission_required = 'network.delete_ipaddress'


class UserIpAddressRemove(PermissionRequiredMixin, DeleteView):
    template_name = 'users/unassign_ipaddress.html'
    model = IpAddress
    permission_required = 'users.change_user'

    def get(self, request, *args, **kwargs):
        context = {}
        context["user"] = get_object_or_404(Lageruser, pk=kwargs["pk"])
        context["ipaddress"] = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")),
            (reverse("userprofile", kwargs={"pk": context["user"].pk}), str(context["user"])),
            ("", _("Unassign IP-Address"))]
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(Lageruser, pk=kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        ipaddress.user = None
        reversion.set_comment(_("Removed from User {0}".format(str(user))))
        ipaddress.save()

        return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": user.pk}))


class UserIpAddress(PermissionRequiredMixin, FormView):
    template_name = 'devices/assign_ipaddress.html'
    form_class = UserIpAddressForm
    success_url = "/devices"
    permission_required = 'users.change_user'

    def dispatch(self, request, **kwargs):
        self.object = get_object_or_404(Lageruser, pk=self.kwargs['pk'])
        return super().dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")),
            (reverse("userprofile", kwargs={"pk": self.object.pk}), str(self.object)),
            ("", _("Assign IP-Addresses"))]
        return context

    def form_valid(self, form):
        ipaddresses = form.cleaned_data["ipaddresses"]
        reversion.set_comment(_("Assigned to User {0}").format(str(self.object)))
        for ipaddress in ipaddresses:
            ipaddress.user = self.object
            ipaddress.save()

        return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": self.object.pk}))
