from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from devices.models import *
from network.models import IpAddress
from django.shortcuts import render_to_response

class Home(TemplateView):
	template_name = "home.html"

	def get_context_data(self, **kwargs):
		context = super(Home, self).get_context_data(**kwargs)
		context['device_all'] = Device.objects.all().count()
		context['device_available'] = Device.objects.filter(owner=None).count()
		context['ipaddress_all'] = IpAddress.objects.all().count()
		context['ipaddress_available'] = IpAddress.objects.filter(device=None).count()
		return context

class DeviceList(ListView):
	model = Device
	context_object_name = 'device_list'
	paginate_by = 30

class DeviceDetail(DetailView):
	model = Device
	context_object_name = 'device'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(DeviceDetail, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['ipaddress_list'] = IpAddress.objects.filter(device=context['device'])
		return context

class DeviceCreate(CreateView):
	model = Device
	template_name = 'devices/base_form.html'

class DeviceUpdate(UpdateView):
	model = Device
	template_name = 'devices/base_form.html'

class DeviceDelete(DeleteView):
	model = Device
	success_url = reverse_lazy('device-list')
	template_name = 'devices/base_delete.html'



class TypeList(ListView):
	model = Type
	context_object_name = 'type_list'

class TypeDetail(DetailView):
	model = Type
	context_object_name = 'object'
	template_name = "devices/base_detail.html"

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(TypeDetail, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['device_list'] = Device.objects.filter(devicetype=context["object"])
		return context

class TypeCreate(CreateView):
	model = Type
	template_name = 'devices/base_form.html'

class TypeUpdate(UpdateView):
	model = Type
	template_name = 'devices/base_form.html'

class TypeDelete(DeleteView):
	model = Type
	success_url = reverse_lazy('type-list')
	template_name = 'devices/base_delete.html'



class RoomList(ListView):
	model = Room
	context_object_name = 'room_list'

class RoomDetail(DetailView):
	model = Room
	context_object_name = 'room'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(RoomDetail, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['device_list'] = Device.objects.filter(room=context["room"])
		return context

class RoomCreate(CreateView):
	model = Room
	template_name = 'devices/base_form.html'

class RoomUpdate(UpdateView):
	model = Room
	template_name = 'devices/base_form.html'

class RoomDelete(DeleteView):
	model = Room
	success_url = reverse_lazy('room-list')
	template_name = 'devices/base_delete.html'



class BuildingList(ListView):
	model = Building
	context_object_name = 'building_list'

class BuildingDetail(DetailView):
	model = Building
	context_object_name = 'building'
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(BuildingDetail, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['device_list'] = Device.objects.filter(room__building=context["building"])
		return context

class BuildingCreate(CreateView):
	model = Building
	template_name = 'devices/base_form.html'

class BuildingUpdate(UpdateView):
	model = Building
	template_name = 'devices/base_form.html'

class BuildingDelete(DeleteView):
	model = Building
	success_url = reverse_lazy('building-list')
	template_name = 'devices/base_delete.html'



class ManufacturerList(ListView):
	model = Manufacturer
	context_object_name = 'manufacturer_list'

class ManufacturerDetail(DetailView):
	model = Manufacturer
	context_object_name = 'object'
	template_name = "devices/base_detail.html"

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(ManufacturerDetail, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['device_list'] = Device.objects.filter(manufacturer=context["object"])
		return context

class ManufacturerCreate(CreateView):
	model = Manufacturer
	template_name = 'devices/base_form.html'

class ManufacturerUpdate(UpdateView):
	model = Manufacturer
	template_name = 'devices/base_form.html'

class ManufacturerDelete(DeleteView):
	model = Manufacturer
	success_url = reverse_lazy('manufacturer-list')
	template_name = 'devices/base_delete.html'

class Search(View):

	def post(self, request, *args, **kwargs):
		searchquery = request.POST["searchquery"]
		devices = Device.objects.filter(name__icontains=searchquery)
		context = {
		"device_list":devices,
		"searchquery":searchquery
		}
		return render_to_response('devices/searchresult.html', context, RequestContext(request))
