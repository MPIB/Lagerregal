from django.views.generic import DetailView, TemplateView
from users.models import Lageruser
from reversion.models import Version
from devices.models import Device
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from users.forms import SettingsForm
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

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
        context["breadcrumbs"] = [("", context["profileuser"])]
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
            (reverse("userprofile", kwargs={"pk":self.request.user.pk}), self.request.user),]
        return context

class UsersettingsView(TemplateView):
    template_name = "users/settings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UsersettingsView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        if self.request.method != "POST":
            context['settingsform'] = SettingsForm(initial={"pagelength":self.request.user.pagelength})
        context["breadcrumbs"] = [
            (reverse("userprofile", kwargs={"pk":self.request.user.pk}), self.request.user),
            ("", _("Settings"))]
        return context

    def post(self, request): 
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
            context = self.get_context_data()
            context["settingsform"] = form
            return  render(request, self.template_name, context)