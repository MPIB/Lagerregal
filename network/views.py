from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from network.models import IpAddress
from network.forms import ViewForm, IpAddressForm
from devices.forms import FilterForm
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from Lagerregal.utils import PaginationMixin

class IpAddressList(PaginationMixin, ListView):
    context_object_name = 'ipaddress_list'

    def get_queryset(self):
        self.viewfilter = self.kwargs.pop("filter", "all")
        self.filterstring = self.kwargs.pop("search", "")
        if self.viewfilter == "all":
            addresses = IpAddress.objects.all()
        elif self.viewfilter == "free":
            addresses = IpAddress.objects.filter(device=None, user=None)
        elif self.viewfilter == "used":
            addresses = IpAddress.objects.exclude(device=None, user=None)
        else:
            addresses = IpAddress.objects.all()
        if self.filterstring != "":
            addresses = addresses.filter(address__icontains=self.filterstring)
        return addresses.values("id", "address", "device__pk", "device__name", "user__pk", "user__username", "user__first_name", "user__last_name")

    def get_context_data(self, **kwargs):
        context = super(IpAddressList, self).get_context_data(**kwargs)
        context["viewform"] = ViewForm(initial={'viewfilter': self.viewfilter})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring":self.filterstring})
        else:
            context["filterform"] = FilterForm()
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
                context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(context["ipaddress"], attribute))

        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            (reverse("ipaddress-detail", kwargs={"pk":self.object.pk}), self.object.address)]
        return context

class IpAddressCreate(CreateView):
    model = IpAddress
    form_class = IpAddressForm
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IpAddressCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new"
        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            ("", _("Create new IP-Address"))]
        return context

    def form_valid(self, form):
        form.instance.address = ".".join([(x.lstrip("0") if x != "0" else x) for x in form.cleaned_data["address"].split(".")])
        return super(IpAddressCreate, self).form_valid(form)


class IpAddressUpdate(UpdateView):
    model = IpAddress
    form_class = IpAddressForm
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IpAddressUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            (reverse("ipaddress-detail", kwargs={"pk":self.object.pk}), self.object.address),
            ("", _("Edit"))]
        return context

    def form_valid(self, form):
        form.instance.address = ".".join([(x.lstrip("0") if x != "0" else x) for x in form.cleaned_data["address"].split(".")])
        return super(IpAddressUpdate, self).form_valid(form)


class IpAddressDelete(DeleteView):
    model = IpAddress
    success_url = reverse_lazy('ipaddress-list')

class IpAdressAssign(FormView):
    model = IpAddress
    success_url = reverse_lazy('device-list')
