from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from network.models import *
from network.forms import *

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

class IpAddressUpdate(UpdateView):
	model = IpAddress
	template_name = 'devices/base_form.html'

class IpAddressDelete(DeleteView):
	model = IpAddress
	success_url = reverse_lazy('ipaddress-list')

class IpAdressAssign(FormView):
	model = IpAddress
	success_url = reverse_lazy('device-list')