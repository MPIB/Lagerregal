from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View, FormView
from django.template import RequestContext, loader, Context
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy, reverse
from devices.models import Device, Template, Room, Building, Manufacturer, Lending
from devicetypes.models import Type, TypeAttribute
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.formats import localize
from django.contrib import messages
from devicetypes.forms import TypeForm
from django.shortcuts import render

class TypeList(ListView):
    model = Type
    context_object_name = 'type_list'
    paginate_by = 30

class TypeDetail(DetailView):
    model = Type
    context_object_name = 'object'
    template_name = "devicetypes/type_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TypeDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Type.objects.exclude(pk=context["object"].pk)
        context['device_list'] = Device.objects.filter(devicetype=context["object"], archived=None)
        context["attribute_list"] = TypeAttribute.objects.filter(devicetype=context["object"])
        return context

class TypeCreate(CreateView):
    form_class = TypeForm
    template_name = 'devicetypes/type_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TypeCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Create new Devicetype"
        context['type'] = "type"
        return context

    def form_valid(self, form):
        newobject = form.save()
        for key, value in form.cleaned_data.iteritems():
            if key.startswith("extra_field_") and value != "":
                attribute = TypeAttribute()
                attribute.name = value
                attribute.devicetype = newobject
                attribute.save()
        return HttpResponseRedirect(newobject.get_absolute_url())

class TypeUpdate(UpdateView):
    form_class = TypeForm
    model = Type
    template_name = 'devicetypes/type_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TypeUpdate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = "Update"
        context["attribute_list"] = TypeAttribute.objects.filter(devicetype=context["object"])
        context["form"].fields.pop("extra_field_0")
        context["form"]["extra_fieldcount"].initial = context["attribute_list"].count()
        return context

class TypeDelete(DeleteView):
    model = Type
    success_url = reverse_lazy('type-list')
    template_name = 'devices/base_delete.html'

class TypeMerge(View):
    model = Type

    def get(self, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        return render_to_response('devices/base_merge.html', context, RequestContext(self.request))

    def post(self, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])
        devices = Device.objects.filter(devicetype=oldobject)
        for device in devices:
            device.devicetype = newobject
            device.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())



class TypeAttributeCreate(CreateView):
    model = TypeAttribute
    template_name = 'devices/base_form.html'


class TypeAttributeUpdate(UpdateView):
    model = TypeAttribute
    template_name = 'devices/base_form.html'

class TypeAttributeDelete(DeleteView):
    model = TypeAttribute
    success_url = reverse_lazy('type-list')
    template_name = 'devices/base_delete.html'

    def post(self, request, **kwargs):
        self.next = request.POST["next"]
        return  super(TypeAttributeDelete, self).post(request, **kwargs)


    def get_success_url(self):
        return self.next