from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

import reversion
from reversion.models import Version

from devices.forms import VIEWSORTING
from devices.forms import DepartmentFilterForm
from devices.forms import FilterForm
from devices.forms import ViewForm
from devices.models import Device
from devices.models import Lending
from Lagerregal.utils import PaginationMixin
from network.forms import UserIpAddressForm
from network.models import IpAddress
from users.forms import AvatarForm
from users.forms import DepartmentAddUserForm
from users.forms import SettingsForm
from users.mixins import PermissionRequiredMixin
from users.models import Department
from users.models import DepartmentUser
from users.models import Lageruser


class UserList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Lageruser
    context_object_name = 'user_list'
    template_name = "users/user_list.html"
    permission_required = "users.view_lageruser"

    def get_queryset(self):
        users = Lageruser.objects.filter(is_active=True)
        self.filterstring = self.request.GET.get("filter", "")

        # filtering by department
        if self.request.user.departments.count() > 0:
            self.departmentfilter = self.request.GET.get("department", "my")
        else:
            self.departmentfilter = self.request.GET.get("department", "all")

        if self.departmentfilter != "all" and self.departmentfilter != "my":
            users = users.filter(departments__id=self.departmentfilter).distinct()
        elif self.departmentfilter == "my":
            users = users.filter(departments__in=self.request.user.departments.all()).distinct()

        # filter by given filter string
        if self.filterstring != "":
            users = users.filter(Q(username__icontains=self.filterstring) | Q(first_name__icontains=self.filterstring) | Q(last_name__icontains=self.filterstring))

        return users

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # adds "Users" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")), ]
        context["filterform"] = DepartmentFilterForm(initial={"filter": self.filterstring, "department": self.departmentfilter})

        # add page number to breadcrumbs if there are multiple pages
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])

        return context


class ProfileBaseView(DetailView):
    model = Lageruser
    context_object_name = 'profileuser'
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # shows list of edits made by user
        context['edits'] = Version.objects\
            .select_related("revision", "revision__user")\
            .filter(
                content_type_id=ContentType.objects.get(model='device').id,
                revision__user=context["profileuser"])\
            .order_by("-pk")

        # shows list of user lendings
        context['lendings'] = Lending.objects.select_related("device", "device__room", "device__room__building",
                                                             "owner").filter(owner=context["profileuser"],
                                                                             returndate=None)
        context['lendhistory'] = Lending.objects.filter(owner=self.object).order_by('-lenddate').exclude(returndate=None)

        # shows list of user related ip-adresses
        context['ipaddresses'] = self.object.ipaddress_set.all()
        context['ipaddressform'] = UserIpAddressForm()
        context["ipaddressform"].fields["ipaddresses"].queryset = IpAddress.objects.filter(department__in=self.object.departments.all(), device=None, user=None)

        # shows list of users permission (group permission, user permission)
        context["permission_list"] = Permission.objects.all().values("name", "codename", "content_type__app_label")
        context["userperms"] = [x[0] for x in self.object.user_permissions.values_list("codename")]
        context["groupperms"] = [x.split(".")[1] for x in self.object.get_group_permissions()]

        context["merge_list"] = Lageruser.objects.exclude(pk=context["object"].pk, is_active=True).order_by("last_name")

        # adds user name to breadcrumbs
        context["breadcrumbs"] = [(reverse("user-list"), _("Users")), ("", self.object)]

        return context


class ProfileView(PermissionRequiredMixin, ProfileBaseView):
    permission_required = "users.view_lageruser"


class UserprofileView(ProfileBaseView):

    def get_object(self, queryset=None):
        return self.request.user


class TransferOwnershipView(PermissionRequiredMixin, View):
    model = Lageruser
    permission_required = 'users.change_lageruser'

    def get(self, request, *args, **kwargs):
        context = {"old_user": get_object_or_404(self.model, pk=kwargs["oldpk"]),
                   "new_user": get_object_or_404(self.model, pk=kwargs["newpk"])}

        # adds "Merge with devicetype name" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")),
            (reverse("userprofile", kwargs={"pk": context["old_user"].pk}), context["old_user"]),
            ("", _("Transfer Ownerships to {0}".format(context["new_user"])))]

        return render(request, 'users/transfer_ownershop.html', context)

    def post(self, request, *args, **kwargs):
        old_user = get_object_or_404(self.model, pk=kwargs["oldpk"])
        new_user = get_object_or_404(self.model, pk=kwargs["newpk"])

        for device in Device.objects.filter(Q(creator=old_user) | Q(contact=old_user)):
            if device.creator is old_user:
                device.creator = new_user
            if device.contact is old_user:
                device.contact = new_user
            reversion.set_comment(_("Transferred Ownerships from {0} to {1}".format(old_user, new_user)))
            device.save()

        for address in IpAddress.objects.filter(user=old_user):
            address.user = new_user
            reversion.set_comment(_("Transferred Ownership from {0} to {1}".format(old_user, new_user)))
            address.save()

        for lending in Lending.objects.filter(owner=old_user):
            lending.owner = new_user
            reversion.set_comment(_("Transferred Ownership from {0} to {1}".format(old_user, new_user)))
            lending.save()

        return HttpResponseRedirect(new_user.get_absolute_url())


class DeactivateUserView(PermissionRequiredMixin, View):
    model = Lageruser
    permission_required = 'users.delete_lageruser'

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(self.model, pk=kwargs["pk"])
        user.is_active = False
        user.save()
        return HttpResponseRedirect(user.get_absolute_url())


class UsersettingsView(TemplateView):
    template_name = "users/settings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        if self.request.method != "POST":
            context['settingsform'] = SettingsForm(instance=self.request.user)
            context['avatarform'] = AvatarForm(instance=self.request.user)

        if "settingsform" in context:
            context['settingsform'].fields["main_department"].queryset = self.request.user.departments.all()

        # adds "Settings" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("userprofile", kwargs={"pk": self.request.user.pk}), self.request.user),
            ("", _("Settings"))]

        return context

    def post(self, request):
        context = self.get_context_data()
        context["settingsform"] = SettingsForm(instance=request.user)
        context["avatarform"] = AvatarForm(instance=request.user)
        context['settingsform'].fields["main_department"].queryset = self.request.user.departments.all()

        # handle language settings and use saved settings of user as default
        if "language" in request.POST:
            request.user.language = request.POST["language"]
            request.user.save()
            return HttpResponseRedirect(reverse("usersettings"))

        # handle pagelength/ timezone/ theme settings and use saved settings of user as default
        elif "pagelength" in request.POST or "timezone" in request.POST or "theme" in request.POST:
            form = SettingsForm(request.POST)
            if form.is_valid():
                changed_data = False

                # change of pagelength settings
                if request.user.pagelength != form.cleaned_data["pagelength"]:
                    request.user.pagelength = form.cleaned_data["pagelength"]
                    changed_data = True

                # change of timezone settings
                if request.user.timezone != form.cleaned_data["timezone"]:
                    request.user.timezone = form.cleaned_data["timezone"]
                    changed_data = True

                # change of main department settings
                if request.user.main_department != form.cleaned_data["main_department"]:
                    request.user.main_department = form.cleaned_data["main_department"]
                    changed_data = True

                # change of theme settings
                if request.user.theme != form.cleaned_data["theme"]:
                    request.user.theme = form.cleaned_data["theme"]
                    changed_data = True

                # save changes
                if changed_data:
                    request.user.save()

                # save success message
                messages.success(self.request, _('Settings were successfully updated'))
            context["settingsform"] = form

        # handle given avatar
        elif "avatar" in request.FILES or "avatar" in request.POST:
            form = AvatarForm(request.POST, request.FILES, instance=request.user)

            if form.is_valid():
                if form.cleaned_data["avatar_clear"] and request.user.avatar is not None:
                    request.user.avatar.delete()
                    request.user.avatar = None
                    request.user.save()
                form.save()
            context["avatarform"] = form

        return render(request, self.template_name, context)


class DepartmentList(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Department
    context_object_name = 'department_list'
    permission_required = "users.view_department"

    def get_queryset(self):
        sections = Department.objects.all()
        self.filterstring = self.request.GET.get("filter", None)
        if self.filterstring:
            sections = sections.filter(name__icontains=self.filterstring)
        self.viewsorting = self.request.GET.get("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            sections = sections.order_by(self.viewsorting)
        return sections

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments"))]
        context["viewform"] = ViewForm(initial={"sorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filter": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class DepartmentCreate(PermissionRequiredMixin, CreateView):
    model = Department
    success_url = reverse_lazy('department-list')
    template_name = 'devices/base_form.html'
    fields = "__all__"
    permission_required = "users.add_department"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['type'] = "section"
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Departments")),
            ("", _("Create new department"))]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        department_user = DepartmentUser(user=self.request.user, department=self.object, role="a")
        department_user.save()
        return response


class DepartmentDetail(PermissionRequiredMixin, DetailView):
    model = Department
    context_object_name = 'department'
    template_name = "users/department_detail.html"
    permission_required = "users.view_department"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department_users'] = DepartmentUser.objects.select_related("user").filter(department=self.object)

        if "department" in settings.LABEL_TEMPLATES:
            context["label_js"] = ""
            for attribute in settings.LABEL_TEMPLATES["section"][1]:
                if attribute == "id":
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1:07d}');".format(attribute, getattr(
                        context["department"], attribute))
                else:
                    context["label_js"] += "\n" + "label.setObjectText('{0}', '{1}');".format(attribute, getattr(
                        context["department"], attribute))
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments")),
            (reverse("department-detail", kwargs={"pk": context["object"].pk}), context["object"].name)]
        return context


class DepartmentUpdate(PermissionRequiredMixin, UpdateView):
    model = Department
    fields = "__all__"
    success_url = reverse_lazy('department-list')
    template_name = 'devices/base_form.html'
    permission_required = 'users.change_department'

    def get_permission_object(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments")),
            (reverse("department-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Edit"))]
        return context


class DepartmentDelete(PermissionRequiredMixin, DeleteView):
    model = Department
    success_url = reverse_lazy('department-list')
    template_name = 'devices/base_delete.html'
    permission_required = 'users.delete_department'

    def get_permission_object(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments")),
            (reverse("department-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Delete"))]
        return context


class DepartmentAddUser(FormView):
    form_class = DepartmentAddUserForm
    template_name = 'devices/base_form.html'

    def get_success_url(self):
        return reverse("department-detail", kwargs={"pk": self.department.pk})

    def get_context_data(self, **kwargs):
        self.department = get_object_or_404(Department, id=self.kwargs.get("pk", ""))
        if not self.request.user.has_perm("users.add_department_user", self.department):
            raise PermissionDenied
        context = super().get_context_data(**kwargs)
        context["form"].fields["department"].initial = self.department
        context["form"].fields["user"].queryset = Lageruser.objects.exclude(departments__id=self.department.id)

        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments")),
            (reverse("department-detail", kwargs={"pk": self.department.pk}), self.department),
            ("", _("Add User"))]
        return context

    def form_valid(self, form):
        self.department = get_object_or_404(Department, id=self.kwargs.get("pk", ""))
        if self.department not in form.cleaned_data["user"].departments.all():
            department_user = DepartmentUser(
                user=form.cleaned_data["user"],
                department=form.cleaned_data["department"],
                role=form.cleaned_data["role"],
            )
            department_user.save()
            if form.cleaned_data["user"].main_department is None:
                form.cleaned_data["user"].main_department = form.cleaned_data["department"]

        return HttpResponseRedirect(reverse("department-detail", kwargs={"pk": self.department.pk}))


class DepartmentDeleteUser(PermissionRequiredMixin, DeleteView):
    model = DepartmentUser
    template_name = 'devices/base_delete.html'
    permission_required = 'users.delete_department_user'

    def get_permission_object(self):
        return self.get_object()

    def get_success_url(self):
        return reverse("department-detail", kwargs={"pk": self.object.department.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments")),
            (reverse("department-detail", kwargs={"pk": self.object.department.pk}), self.object.department),
            ("", _("Remove User"))]
        return context
