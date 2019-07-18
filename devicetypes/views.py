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
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import View

from reversion import revisions as reversion

from devices.forms import VIEWSORTING
from devices.forms import FilterForm
from devices.forms import ViewForm
from devices.models import Device
from devicetypes.forms import TypeForm
from devicetypes.models import Type
from devicetypes.models import TypeAttribute
from Lagerregal.utils import PaginationMixin
from users.mixins import PermissionRequiredMixin


class TypeList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Type
    context_object_name = 'type_list'
    permission_required = 'devicetypes.view_type'

    def get_queryset(self):
        '''method for query all devicetypes and present the results depending on existing filter'''
        devicetype = Type.objects.all()

        # filtering with existing filterstring
        self.filterstring = self.request.GET.get("filter", None)
        if self.filterstring:
            devicetype = devicetype.filter(name__icontains=self.filterstring)

        # sort list of results (name or ID ascending or descending)
        self.viewsorting = self.request.GET.get("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            devicetype = devicetype.order_by(self.viewsorting)

        return devicetype

    def get_context_data(self, **kwargs):
        '''method for getting context data for filtering, viewsorting and breadcrumbs'''
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")), ]
        context["viewform"] = ViewForm(initial={"sorting": self.viewsorting})

        # filtering
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filter": self.filterstring})
        else:
            context["filterform"] = FilterForm()

        # show page number in breadcrumbs
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])

        return context


class TypeDetail(PermissionRequiredMixin, DetailView):
    model = Type
    context_object_name = 'object'
    template_name = "devicetypes/type_detail.html"
    permission_required = 'devicetypes.view_type'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        # adds data of related devices and attributes
        context["merge_list"] = Type.objects.exclude(pk=context["object"].pk).order_by("name")
        context['device_list'] = Device.objects.filter(devicetype=context["object"], archived=None, trashed=None)
        context["attribute_list"] = TypeAttribute.objects.filter(devicetype=context["object"])

        # use given label template if existing
        if "type" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["type"][1]:
                context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute,
                                                                                          getattr(context["object"],
                                                                                                  attribute))
        # show chosen type in breadcrumbs
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            (reverse("type-detail", kwargs={"pk": context["object"].pk}), context["object"])]

        return context


class TypeCreate(PermissionRequiredMixin, CreateView):
    form_class = TypeForm
    template_name = 'devicetypes/type_form.html'
    permission_required = 'devicetypes.add_type'

    def get_context_data(self, **kwargs):
        '''method for getting context data and show in breadcrumbs'''
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = _("Create new Devicetype")
        context['type'] = "type"

        # adds "Create new Devicetype" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            ("", _("Create new Devicetype"))]

        return context

    def form_valid(self, form):
        newobject = form.save()

        # creating new attributes to devicetype
        for key, value in form.cleaned_data.items():
            if key.startswith("extra_field_") and value != "":
                attribute = TypeAttribute()
                attribute.name = value
                attribute.devicetype = newobject
                attribute.save()

        return HttpResponseRedirect(newobject.get_absolute_url())


class TypeUpdate(PermissionRequiredMixin, UpdateView):
    form_class = TypeForm
    model = Type
    template_name = 'devicetypes/type_form.html'
    permission_required = 'devicetypes.change_type'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['actionstring'] = _("Update")
        context["attribute_list"] = TypeAttribute.objects.filter(devicetype=context["object"])
        context["form"].fields.pop("extra_field_0")
        context["form"]["extra_fieldcount"].initial = context["attribute_list"].count()

        # adds "Edit" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            (reverse("type-detail", kwargs={"pk": context["object"].pk}), context["object"]),
            ("", _("Edit"))]

        return context


class TypeDelete(PermissionRequiredMixin, DeleteView):
    model = Type
    success_url = reverse_lazy('type-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'devicetypes.delete_type'

    # !!!! there is no forwarding or loading so the code is never run
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(**kwargs)
    #
    #     # should add "Delete" to breadcrumbs
    #     context["breadcrumbs"] = [
    #         (reverse("type-list"), _("Devicetypes")),
    #         (reverse("type-detail", kwargs={"pk": context["object"].pk}), context["object"]),
    #         ("", _("Delete"))]
    #
    #     return context


class TypeMerge(PermissionRequiredMixin, View):
    model = Type
    permission_required = 'devicetypes.change_type'

    def get(self, request, *args, **kwargs):
        context = {}
        context["oldobject"] = get_object_or_404(self.model, pk=kwargs["oldpk"])
        context["newobject"] = get_object_or_404(self.model, pk=kwargs["newpk"])

        # adds "Merge with devicetype name" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("type-list"), _("Devicetypes")),
            (reverse("type-detail", kwargs={"pk": context["oldobject"].pk}), context["oldobject"]),
            ("", _("Merge with {0}".format(context["newobject"])))]

        return render(request, 'devices/base_merge.html', context)

    def post(self, request, *args, **kwargs):
        oldobject = get_object_or_404(self.model, pk=kwargs["oldpk"])
        newobject = get_object_or_404(self.model, pk=kwargs["newpk"])

        # adds all devices of old devicetype to new devicetype
        devices = Device.objects.filter(devicetype=oldobject)
        for device in devices:
            device.devicetype = newobject
            reversion.set_comment(_("Merged Devicetype {0} into {1}".format(oldobject, newobject)))
            device.save()

        # adds all attributes of old devicetype to new devicetype
        attributes = TypeAttribute.objects.filter(devicetype=oldobject)
        for attribute in attributes:
            attribute.devicetype = newobject
            attribute.save()
        oldobject.delete()

        return HttpResponseRedirect(newobject.get_absolute_url())


######################################################################################################################
#                                           attribute related views                                                  #
######################################################################################################################

class TypeAttributeCreate(PermissionRequiredMixin, CreateView):
    model = TypeAttribute
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devicetypes.change_type'


class TypeAttributeUpdate(PermissionRequiredMixin, UpdateView):
    model = TypeAttribute
    template_name = 'devices/base_form.html'
    fields = '__all__'
    permission_required = 'devicetypes.change_type'

    def post(self, request, *args, **kwargs):
        self.success_url = reverse('type-detail',
                                   kwargs={'pk': request.POST['devicetype']})
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url


class TypeAttributeDelete(PermissionRequiredMixin, DeleteView):
    model = TypeAttribute
    success_url = reverse_lazy('type-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'devicetypes.change_type'

    def post(self, request, *args, **kwargs):
        self.next = request.POST["next"]
        return super().post(request, **kwargs)

    def get_success_url(self):
        return self.next
