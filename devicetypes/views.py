from __future__ import unicode_literals
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse
from reversion import revisions as reversion
from django.conf import settings

from devices.models import Device
from devicetypes.models import Type, TypeAttribute
from devicetypes.forms import TypeForm
from devices.forms import ViewForm, VIEWSORTING, FilterForm
from Lagerregal.utils import PaginationMixin


class TypeList(PaginationMixin, ListView):
    model = Type
    context_object_name = 'type_list'

    def get_queryset(self):
        devicetype = Type.objects.all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            devicetype = devicetype.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devicetype = devicetype.order_by(self.viewsorting)
        return devicetype

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TypeList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")), ]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class TypeDetail(DetailView):
    model = Type
    context_object_name = 'object'
    template_name = "devicetypes/type_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TypeDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["merge_list"] = Type.objects.exclude(pk=context["object"].pk).order_by("name")
        context['device_list'] = Device.objects.filter(devicetype=context["object"], archived=None, trashed=None)
        context["attribute_list"] = TypeAttribute.objects.filter(devicetype=context["object"])

        if "type" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["type"][1]:
                context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute,
                                                                                          getattr(context["object"],
                                                                                                  attribute))

        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            (reverse("type-detail", kwargs={"pk": context["object"].pk}), context["object"])]
        return context


class TypeCreate(CreateView):
    form_class = TypeForm
    template_name = 'devicetypes/type_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TypeCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = _("Create new Devicetype")
        context['type'] = "type"
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            ("", _("Create new Devicetype"))]
        return context

    def form_valid(self, form):
        newobject = form.save()
        for key, value in form.cleaned_data.items():
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
        context['actionstring'] = _("Update")
        context["attribute_list"] = TypeAttribute.objects.filter(devicetype=context["object"])
        context["form"].fields.pop("extra_field_0")
        context["form"]["extra_fieldcount"].initial = context["attribute_list"].count()
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            (reverse("type-detail", kwargs={"pk": context["object"].pk}), context["object"]),
            ("", _("Edit"))]
        return context


class TypeDelete(DeleteView):
    model = Type
    success_url = reverse_lazy('type-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TypeDelete, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            (reverse("type-detail", kwargs={"pk": context["object"].pk}), context["object"]),
            ("", _("Delete"))]
        return context


class TypeMerge(View):
    model = Type

    def get(self, request, *args, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            (reverse("type-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"]),
            ("", _("Merge with {0}".format(context["newobject"])))]
        return render(request, 'devices/base_merge.html', context)

    def post(self, request, *args, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])

        devices = Device.objects.filter(devicetype=oldobject)
        for device in devices:
            device.devicetype = newobject
            reversion.set_comment(_("Merged Devicetype {0} into {1}".format(oldobject, newobject)))
            device.save()

        attributes = TypeAttribute.objects.filter(devicetype=oldobject)
        for attribute in attributes:
            attribute.devicetype = newobject
            attribute.save()
        oldobject.delete()
        return HttpResponseRedirect(newobject.get_absolute_url())


class TypeAttributeCreate(CreateView):
    model = TypeAttribute
    template_name = 'devices/base_form.html'
    fields = '__all__'


class TypeAttributeUpdate(UpdateView):
    model = TypeAttribute
    template_name = 'devices/base_form.html'
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        self.success_url = reverse('type-detail',
                                   kwargs={'pk': request.POST['devicetype']})
        return super(TypeAttributeUpdate, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url


class TypeAttributeDelete(DeleteView):
    model = TypeAttribute
    success_url = reverse_lazy('type-list')
    template_name = 'devices/base_delete.html'

    def post(self, request, *args, **kwargs):
        self.next = request.POST["next"]
        return super(TypeAttributeDelete, self).post(request, **kwargs)

    def get_success_url(self):
        return self.next
