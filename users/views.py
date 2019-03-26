from __future__ import unicode_literals
from django.views.generic import DetailView, TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from permission.decorators import permission_required
from reversion.models import Version

from users.models import Lageruser, Department, DepartmentUser
from devices.models import Lending
from users.forms import SettingsForm, AvatarForm, DepartmentAddUserForm
from Lagerregal import settings
from Lagerregal.utils import PaginationMixin
from network.models import IpAddress
from network.forms import UserIpAddressForm
from devices.forms import ViewForm, VIEWSORTING, DepartmentFilterForm, FilterForm


class UserList(PaginationMixin, ListView):
    model = Lageruser
    context_object_name = 'user_list'
    template_name = "users/user_list.html"

    def get_queryset(self):
        users = Lageruser.objects.all()
        self.filterstring = self.kwargs.pop("filter", "")

        # filtering by department
        if self.request.user.departments.count() > 0:
            self.departmentfilter = self.kwargs.get("department", "my")
        else:
            self.departmentfilter = self.kwargs.get("department", "all")

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
        context = super(UserList, self).get_context_data(**kwargs)

        # adds "Users" to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")), ]
        context["filterform"] = DepartmentFilterForm(initial={"filterstring": self.filterstring, "departmentfilter": self.departmentfilter})

        # add page number to breadcrumbs if there are multiple pages
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])

        return context


class ProfileView(DetailView):
    model = Lageruser
    context_object_name = 'profileuser'

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        # shows list of edits made by user
        context['edits'] = Version.objects.select_related("revision", "revision__user"
        ).filter(content_type_id=ContentType.objects.get(model='device').id,
                 revision__user=context["profileuser"]).order_by("-pk")

        # shows list of user lendings
        context['lendings'] = Lending.objects.select_related("device", "device__room", "device__room__building",
                                                             "owner").filter(owner=context["profileuser"],
                                                                             returndate=None)
        context['lendhistory'] = Lending.objects.filter(owner=context["profileuser"]).order_by('-lenddate').exclude(returndate=None)
        # shows list of user related ip-adresses
        context['ipaddresses'] = IpAddress.objects.filter(user=context["profileuser"])
        context['ipaddressform'] = UserIpAddressForm()
        context["ipaddressform"].fields["ipaddresses"].queryset = IpAddress.objects.filter(device=None,
            user=None).filter(Q(department__in=self.object.departments.all()) | Q(department=None))
        # shows list of users permission (group permission, user permission)
        context["permission_list"] = Permission.objects.all().values("name", "codename", "content_type__app_label")
        context["userperms"] = [x[0] for x in context["profileuser"].user_permissions.values_list("codename")]
        context["groupperms"] = [x.split(".")[1] for x in context["profileuser"].get_group_permissions()]

        # adds username to breadcrumbs
        context["breadcrumbs"] = [(reverse("user-list"), _("Users")), ("", context["profileuser"])]

        return context


class UserprofileView(TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserprofileView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["profileuser"] = self.request.user

        # shows list of edits made by user
        context['edits'] = Version.objects.select_related("revision", "revision__user"
        ).filter(content_type_id=ContentType.objects.get(model='device').id,
                 revision__user=context["profileuser"]).order_by("-pk")

        # shows list users lendings
        context['lendings'] = Lending.objects.select_related("device", "device__room", "device__room__building",
                                                             "owner").filter(owner=context["profileuser"],
                                                                             returndate=None)

        # shows user related ip-adresses
        context['ipaddresses'] = IpAddress.objects.filter(user=context["profileuser"])
        context['ipaddressform'] = UserIpAddressForm()

        # shows list of users permissions (group permissions, user permissions)
        context["permission_list"] = Permission.objects.all().values("name", "codename", "content_type__app_label")
        context["userperms"] = [x[0] for x in context["profileuser"].user_permissions.values_list("codename")]
        context["groupperms"] = [x.split(".")[1] for x in context["profileuser"].get_group_permissions()]

        # adds user name to breadcrumbs
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")),
            (reverse("userprofile", kwargs={"pk": self.request.user.pk}), self.request.user), ]

        return context


class UsersettingsView(TemplateView):
    template_name = "users/settings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UsersettingsView, self).get_context_data(**kwargs)
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
            translation.activate(request.POST["language"])
            request.session[translation.LANGUAGE_SESSION_KEY] = request.POST["language"]
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
            if request.user.avatar:
                tempavatar = request.user.avatar
            else:
                tempavatar = None

            form = AvatarForm(request.POST, request.FILES, instance=request.user)

            if form.is_valid():
                if form.cleaned_data["avatar_clear"] and request.user.avatar is not None:
                    request.user.avatar.delete()
                    request.user.avatar = None
                    request.user.save()
                if tempavatar is not None:
                    tempavatar.storage.delete(tempavatar)
                form.save()
            context["avatarform"] = form

        return render(request, self.template_name, context)


#######################################################################################################################
#                                                       Login                                                         #
#######################################################################################################################
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    if request.method == "POST":
        redirect_to = request.GET.get(redirect_field_name, '')
        form = authentication_form(data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url("/")

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            request.session['django_language'] = request.user.language
            return HttpResponseRedirect(redirect_to)
    else:
        redirect_to = request.POST.get(redirect_field_name, '')
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }

    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


class DepartmentList(PaginationMixin, ListView):
    model = Department
    context_object_name = 'department_list'

    def get_queryset(self):
        sections = Department.objects.all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            sections = sections.filter(name__icontains=self.filterstring)
        self.viewsorting = self.kwargs.pop("sorting", "name")
        if self.viewsorting in [s[0] for s in VIEWSORTING]:
            sections = sections.order_by(self.viewsorting)
        return sections

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DepartmentList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments"))]
        context["viewform"] = ViewForm(initial={"viewsorting": self.viewsorting})
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring": self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context


class DepartmentCreate(CreateView):
    model = Department
    success_url = reverse_lazy('department-list')
    template_name = 'devices/base_form.html'
    fields = "__all__"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DepartmentCreate, self).get_context_data(**kwargs)
        context['type'] = "section"
        context["breadcrumbs"] = [
            (reverse("section-list"), _("Departments")),
            ("", _("Create new department"))]
        return context

    def form_valid(self, form):
        response = super(DepartmentCreate, self).form_valid(form)
        department_user = DepartmentUser(user=self.request.user, department=self.object, role="a")
        department_user.save()
        return response


class DepartmentDetail(DetailView):
    model = Department
    context_object_name = 'department'
    template_name = "users/department_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DepartmentDetail, self).get_context_data(**kwargs)
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


@permission_required('users.change_department', raise_exception=True)
class DepartmentUpdate(UpdateView):
    model = Department
    success_url = reverse_lazy('department-list')
    template_name = 'devices/base_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DepartmentUpdate, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments")),
            (reverse("department-detail", kwargs={"pk": self.object.pk}), self.object),
            ("", _("Edit"))]
        return context


@permission_required('users.delete_department', raise_exception=True)
class DepartmentDelete(DeleteView):
    model = Department
    success_url = reverse_lazy('department-list')
    template_name = 'devices/base_delete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DepartmentDelete, self).get_context_data(**kwargs)
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
        context = super(DepartmentAddUser, self).get_context_data(**kwargs)
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
            department_user = DepartmentUser(user=form.cleaned_data["user"], department=form.cleaned_data["department"],
                                            role=form.cleaned_data["role"])
            department_user.save()
            if form.cleaned_data["user"].main_department is None:
                form.cleaned_data["user"].main_department = form.cleaned_data["department"]

        return HttpResponseRedirect(reverse("department-detail", kwargs={"pk": self.department.pk}))


@permission_required('users.delete_department_user', raise_exception=True)
class DepartmentDeleteUser(DeleteView):
    model = DepartmentUser
    template_name = 'devices/base_delete.html'

    def get_success_url(self):
        return reverse("department-detail", kwargs={"pk": self.object.department.pk})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DepartmentDeleteUser, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("department-list"), _("Departments")),
            (reverse("department-detail", kwargs={"pk": self.object.department.pk}), self.object.department),
            ("", _("Remove User"))]
        return context
