from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View, FormView
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from devices.models import *
from network.models import IpAddress
from django.shortcuts import render_to_response
from rest_framework import renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from reversion.models import Version
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.formats import localize
from django.contrib import messages
from devices.forms import IpAddressForm, SearchForm
import datetime

@api_view(('GET',))
def api_root(request, format=None):
	return Response({
	})


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
		context['ipaddress_available'] = IpAddress.objects.filter(device=None)
		context['version_list'] = reversion.get_unique_for_object(context["device"])
		context['ipaddressform'] = IpAddressForm()
		return context

class DeviceIpAddressRemove(DeleteView):
	template_name = 'devices/unassign_ipaddress.html'
	model=IpAddress

	def get(self, request, *args, **kwargs):
		context = {}
		context["device"] = get_object_or_404(Device, pk=kwargs["pk"])
		context["ipaddress"] = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
		return render_to_response(self.template_name, context, RequestContext(request))


	def post(self, request, *args, **kwargs):
		device = get_object_or_404(Device, pk=kwargs["pk"])
		ipaddress = get_object_or_404(IpAddress, pk=kwargs["ipaddress"])
		ipaddress.device = None
		ipaddress.save()

		return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))


class DeviceIpAddress(FormView):
	template_name = 'devices/assign_ipaddress.html'
	form_class = IpAddressForm
	success_url = "/devices"

	def form_valid(self, form):
		ipaddresses = form.cleaned_data["ipaddresses"]
		device = form.cleaned_data["device"]
		for ipaddress in ipaddresses:
			ipaddress.device=device
			ipaddress.save()
		return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceHistory(View):

	def get(self, request, *args, **kwargs):
		deviceid = kwargs["pk"]
		revisionid = kwargs["revision"]
		device = get_object_or_404(Device, pk=deviceid)
		version = get_object_or_404(Version, pk=revisionid)
		context = {"version":version, "device":version.field_dict}
		return render_to_response('devices/device_history.html', context, RequestContext(request))

	def post(self, request, *args, **kwargs):
		deviceid = kwargs["pk"]
		revisionid = kwargs["revision"]
		device = get_object_or_404(Device, pk=deviceid)
		version = get_object_or_404(Version, pk=revisionid)
		version.revision.revert()
		reversion.set_comment("Reverted to version from {}".format(localize(version.revision.date_created)))
		messages.success(request, 'Successfully reverted object')
		return HttpResponseRedirect(reverse("device-detail", kwargs={"pk":device.pk}))

class DeviceHistoryList(View):

	def get(self, request, *args, **kwargs):
		deviceid = kwargs["pk"]
		device = get_object_or_404(Device, pk=deviceid)
		version_list = reversion.get_unique_for_object(device)
		context = {"version_list":version_list, "device":device}
		return render_to_response('devices/device_history_list.html', context, RequestContext(request))


class DeviceCreate(CreateView):
	model = Device
	template_name = 'devices/base_form.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(DeviceCreate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Create new"
		return context

class DeviceUpdate(UpdateView):
	model = Device
	template_name = 'devices/base_form.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(DeviceUpdate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Update"
		return context

class DeviceDelete(DeleteView):
	model = Device
	success_url = reverse_lazy('device-list')
	template_name = 'devices/base_delete.html'



class TypeList(ListView):
	model = Type
	context_object_name = 'type_list'
	paginate_by = 30

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

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(TypeCreate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Create new"
		return context

class TypeUpdate(UpdateView):
	model = Type
	template_name = 'devices/base_form.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(TypeUpdate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Update"
		return context

class TypeDelete(DeleteView):
	model = Type
	success_url = reverse_lazy('type-list')
	template_name = 'devices/base_delete.html'



class RoomList(ListView):
	model = Room
	context_object_name = 'room_list'
	paginate_by = 30

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

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(RoomCreate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Create new"
		return context

class RoomUpdate(UpdateView):
	model = Room
	template_name = 'devices/base_form.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(RoomUpdate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Update"
		return context

class RoomDelete(DeleteView):
	model = Room
	success_url = reverse_lazy('room-list')
	template_name = 'devices/base_delete.html'



class BuildingList(ListView):
	model = Building
	context_object_name = 'building_list'
	paginate_by = 30

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

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(BuildingCreate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Create new"
		return context

class BuildingUpdate(UpdateView):
	model = Building
	template_name = 'devices/base_form.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(BuildingUpdate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Update"
		return context

class BuildingDelete(DeleteView):
	model = Building
	success_url = reverse_lazy('building-list')
	template_name = 'devices/base_delete.html'



class ManufacturerList(ListView):
	model = Manufacturer
	context_object_name = 'manufacturer_list'
	paginate_by = 30

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

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(ManufacturerCreate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Create new"
		return context

class ManufacturerUpdate(UpdateView):
	model = Manufacturer
	template_name = 'devices/base_form.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(ManufacturerUpdate, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['actionstring'] = "Update"
		return context

class ManufacturerDelete(DeleteView):
	model = Manufacturer
	success_url = reverse_lazy('manufacturer-list')
	template_name = 'devices/base_delete.html'

class Search(FormView):
	template_name = 'devices/search.html'
	form_class = SearchForm

	def form_valid(self, form):
		search = {}
		if form.cleaned_data["name"] != "":
			search["name__" + form.cleaned_data["namemodifier"]] = form.cleaned_data["name"] 
		print form.cleaned_data
		if form.cleaned_data["lender"] != "":
			search["currentlending__owner__username__icontains"] = form.cleaned_data["lender"] 

		if form.cleaned_data["buildnumber"] != "":
			search["buildnumber__" + form.cleaned_data["buildnumbermodifier"]] = form.cleaned_data["buildnumber"] 

		if form.cleaned_data["serialnumber"] != "":
			search["serialnumber__" + form.cleaned_data["serialnumbermodifier"]] = form.cleaned_data["serialnumber"] 

		if form.cleaned_data["macaddress"] != "":
			search["name__" + form.cleaned_data["macaddressmodifier"]] = form.cleaned_data["macaddress"] 

		if form.cleaned_data["devicetype"] != None:
			search["devicetype"] = form.cleaned_data["devicetype"] 

		if form.cleaned_data["manufacturer"] != None:
			search["manufacturer"] = form.cleaned_data["manufacturer"] 

		if form.cleaned_data["room"] != None:
			search["room"] = form.cleaned_data["room"] 

		if form.cleaned_data["ipaddress"] != "":
			search["ipaddress__address__icontains"] = form.cleaned_data["ipaddress"] 

		if form.cleaned_data["overdue"]=="y":
			search["duedate__gt"] = datetime.datetime.now()
		elif form.cleaned_data["overdue"]=="n":
			search["duedate__lt"] = datetime.datetime.now()

		

		devices = Device.objects.filter(**search)

		if form.cleaned_data["available"]=="y":
			devices = devices.filter(owner=None)
		elif form.cleaned_data["available"]=="n":
			devices = devices.exclude(owner=None)

		context = {
		"device_list":devices,
		"form":form
		}
		return render_to_response('devices/searchresult.html', context, RequestContext(self.request))
