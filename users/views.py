from django.views.generic import DetailView, TemplateView, ListView
from users.models import Lageruser
from reversion.models import Version
from devices.models import Device
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from users.forms import SettingsForm, AvatarForm
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.conf import settings
from devices.forms import FilterForm

class UserList(ListView):
    model = Lageruser
    context_object_name = 'user_list'
    template_name = "users/user_list.html"
    
    def get_queryset(self):
        user = Lageruser.objects.all()
        self.filterstring = self.kwargs.pop("filter", None)
        if self.filterstring:
            user = user.filter(username__icontains=self.filterstring)
        return user


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserList, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")),]
        if self.filterstring:
            context["filterform"] = FilterForm(initial={"filterstring":self.filterstring})
        else:
            context["filterform"] = FilterForm()
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.pagelength
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class ProfileView(DetailView):
    model = Lageruser
    context_object_name = 'profileuser'

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['edits'] = Version.objects.filter(content_type_id=ContentType.objects.get(model='device').id, revision__user = context["profileuser"]).order_by("-pk")
        context['devices'] = Device.objects.filter(currentlending__owner = context["profileuser"])
        context["permission_list"] = Permission.objects.all().values("name", "codename", "content_type__app_label")
        context["userperms"] = [x[0] for x in context["profileuser"].user_permissions.values_list("codename")]
        context["groupperms"] = [x.split(".")[1] for x in context["profileuser"].get_group_permissions()]
        print context["groupperms"]
        print context["userperms"]
        print context["permission_list"]
        context["breadcrumbs"] = [(reverse("user-list"), _("Users")), ("", context["profileuser"])]
        return context

class UserprofileView(TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserprofileView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["profileuser"] = self.request.user
        context['edits'] = Version.objects.filter(content_type_id=ContentType.objects.get(model='device').id, revision__user = context["profileuser"]).order_by("-pk")
        context['devices'] = Device.objects.filter(currentlending__owner = context["profileuser"])
        context["breadcrumbs"] = [
            (reverse("user-list"), _("Users")), (reverse("userprofile", kwargs={"pk":self.request.user.pk}), self.request.user),]
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
        context["breadcrumbs"] = [
            (reverse("userprofile", kwargs={"pk":self.request.user.pk}), self.request.user),
            ("", _("Settings"))]
        return context

    def post(self, request):
        context = self.get_context_data()
        context["settingsform"] = SettingsForm(instance=request.user)
        context["avatarform"] = AvatarForm(instance=request.user)
        if "language" in request.POST:
            request.user.language = request.POST["language"]
            request.user.save()
            request.session['django_language'] =request.POST["language"]
            return HttpResponseRedirect(reverse("usersettings"))
        elif "pagelength" in request.POST:
            form = SettingsForm(request.POST)
            if form.is_valid():
                if request.user.pagelength != form.cleaned_data["pagelength"]:
                    request.user.pagelength = request.POST["pagelength"]
                    request.user.save()
                messages.success(self.request, _('Settings were successfully updated'))
            context["settingsform"] = form
        elif "avatar" in request.FILES or "avatar" in request.POST:
            if request.user.avatar:
                tempavatar = request.user.avatar
            else:
                tempavatar = None
            form = AvatarForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                if form.cleaned_data["avatar_clear"] and request.user.avatar != None:
                    request.user.avatar.delete()
                    request.user.avatar = None
                    request.user.save()
                if tempavatar != None:
                    print tempavatar
                    tempavatar.storage.delete(tempavatar)
                form.save()
            context["avatarform"] = form
        return  render(request, self.template_name, context)

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            request.session['django_language'] = request.user.language
            return HttpResponseRedirect(redirect_to)
    else:
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
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
