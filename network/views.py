from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from network.models import IpAddress
from rest_framework import generics
from network.serializers import IpAddressSerializer
from network.forms import ViewForm
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

class IpAddressApiList(generics.ListCreateAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer

class IpAddressApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer

class IpAddressList(ListView):
    context_object_name = 'ipaddress_list'
    
    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

    def get_queryset(self):
        self.viewfilter = self.kwargs.pop("filter", "all")
        if self.viewfilter == "all":
            return IpAddress.objects.all()
        elif self.viewfilter == "free":
            return IpAddress.objects.filter(device=None)
        elif self.viewfilter == "used":
            return IpAddress.objects.exclude(device=None)
        else:
            return IpAddress.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IpAddressList, self).get_context_data(**kwargs)
        context["viewform"] = ViewForm(initial={'viewfilter': self.viewfilter})
        context["breadcrumbs"] = [(reverse("device-list"), _("IP-Addresses"))]
        
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

class IpAddressDetail(DetailView):
    model = IpAddress
    context_object_name = 'ipaddress'

    def get_context_data(self, **kwargs):
        context = super(IpAddressDetail, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("ipaddress-list"), _("IP-Addresses")),
            (reverse("ipaddress-detail", kwargs={"pk":self.object.pk}), self.object.address)]
        return context

class IpAddressCreate(CreateView):
    model = IpAddress
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