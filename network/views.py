# coding: utf-8
from __future__ import unicode_literals

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render

import six
from reversion import revisions as reversion

from network.models import IpAddress
from network.forms import ViewForm, IpAddressForm, UserIpAddressForm
from devices.forms import FilterForm
from Lagerregal.utils import PaginationMixin
from users.models import Lageruser


class IpAddressList(PaginationMixin, ListView):
    context_object_name = 'ipaddress_list'

    def get_queryset(self):
        self.usagefilter = self.kwargs.get("usage", "all")
        self.filterstring = self.kwargs.get("filter", "")
        if self.usagefilter == "all":
            addresses = IpAddress.objects.all()
        elif self.usagefilter == "free":
            addresses = IpAddress.objects.filter(device=None, user=None)
        elif self.usagefilter == "used":
            addresses = IpAddress.objects.exclude(device=None, user=None)
        elif self.usagefilter == "byuser":
            addresses = IpAddress.objects.exclude(user=None).filter(device=None)
        elif self.usagefilter == "bydevice":
            addresses = IpAddress.objects.exclude(device=None).filter(user=None)
        else:
            addresses = IpAddress.objects.all()

        if self.request.user.departments.count() > 0:
            self.departmentfilter = self.kwargs.get("department", "my")
        else:
            self.departmentfilter = self.kwargs.get("department", "all")

        if self.departmentfilter != "all" and self.departmentfilter != "my":
            addresses = addresses.filter(department__id=self.departmentfilter)
        elif self.departmentfilter == "my":
            addresses = addresses.filter(department__in=self.request.user.departments.all())

        if self.filterstring != "":
            addresses = addresses.filter(address__icontains=self.filterstring)
        return addresses.values("id", "address", "device__pk", "device__name", "user__pk", "user__username",
                                "user__first_name", "user__last_name")

    def get_context_data(self, **kwargs):
        context = super(IpAddressList, self).get_context_data(**kwargs)
        context["viewform"] = ViewForm(initial={
            "usagefilter": self.usagefilter,
            "departmentfilter": self.departmentfilter
        })
        context["filterform"] = FilterForm(initial={
            "filterstring": self.filterstring
        })
        context["breadcrumbs"] = [(reverse("device-list"), _("IP-Addresses"))]

        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class IpAddressDetail(DetailView):
    model = IpAddress
    context_object_name = 'ipaddress'

    def get_context_data(self, **kwargs):
        context = super(IpAddressDetail, self).get_context_data(**kwargs)

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


class IpAddressCreate(CreateView):
    model = IpAddress
    form_class = IpAddressForm
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        context = super(IpAddressCreate, self).get_context_data(**kwargs)
        context['actionstring'] = "Create new"
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
        return super(IpAddressCreate, self).form_valid(form)


class IpAddressUpdate(UpdateView):
    model = IpAddress
    form_class = IpAddressForm
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IpAddressUpdate, self).get_context_data(**kwargs)
        context["form"].fields["department"].queryset = self.request.user.departments.all()
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            (reverse("ipaddress-detail", kwargs={"pk": self.object.pk}), self.object.address),
            ("", _("Edit"))]
        return context

    def form_valid(self, form):
        form.instance.address = ".".join(
            [(x.lstrip("0") if x != "0" else x) for x in form.cleaned_data["address"].split(".")])
        return super(IpAddressUpdate, self).form_valid(form)


class IpAddressDelete(DeleteView):
    model = IpAddress
    success_url = reverse_lazy('ipaddress-list')


class IpAdressAssign(FormView):
    model = IpAddress
    success_url = reverse_lazy('device-list')


class UserIpAddressRemove(DeleteView):
    template_name = 'users/unassign_ipaddress.html'
    model = IpAddress

    def get(self, request, *args, **kwargs):
        context = {}
        context["user"] = get_object_or_404(Lageruser, pk=kwargs["pk"])
        context["ipaddress"] = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")),
            (reverse("userprofile", kwargs={"pk": context["user"].pk}), six.text_type(context["user"])),
            ("", _("Unassign IP-Address"))]
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(Lageruser, pk=kwargs["pk"])
        ipaddress = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
        ipaddress.user = None
        reversion.set_comment(_("Removed from User {0}".format(six.text_type(user))))
        ipaddress.save()

        return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": user.pk}))


class UserIpAddress(FormView):
    template_name = 'devices/assign_ipaddress.html'
    form_class = UserIpAddressForm
    success_url = "/devices"

    def get_context_data(self, **kwargs):
        context = super(UserIpAddress, self).get_context_data(**kwargs)
        user = context["form"].cleaned_data["user"]
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")),
            (reverse("userprofile", kwargs={"pk": user.pk}), six.text_type(user)),
            ("", _("Assign IP-Addresses"))]
        return context

    def form_valid(self, form):
        ipaddresses = form.cleaned_data["ipaddresses"]
        user = form.cleaned_data["user"]
        reversion.set_comment(_("Assigned to User {0}").format(six.text_type(user)))
        for ipaddress in ipaddresses:
            ipaddress.user = user
            ipaddress.save()

        return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": user.pk}))
