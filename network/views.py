from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from network.models import IpAddress
from rest_framework import generics
from rest_framework.decorators import api_view
from serializers import IpAddressSerializer

class IpAddressApiList(generics.ListCreateAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer

class IpAddressApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer

class IpAddressList(ListView):
    model = IpAddress
    context_object_name = 'ipaddress_list'
    paginate_by = 30

class IpAddressDetail(DetailView):
    model = IpAddress
    context_object_name = 'ipaddress'

class IpAddressCreate(CreateView):
    model = IpAddress
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IpAddressCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new"
        return context

class IpAddressUpdate(UpdateView):
    model = IpAddress
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IpAddressUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        return context


class IpAddressDelete(DeleteView):
    model = IpAddress
    success_url = reverse_lazy('ipaddress-list')

class IpAdressAssign(FormView):
    model = IpAddress
    success_url = reverse_lazy('device-list')