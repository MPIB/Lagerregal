from django.views.generic import DetailView, TemplateView
from users.models import Lageruser
from reversion.models import Version
from devices.models import Device
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from users.forms import AppearanceForm
from django.utils.translation import ugettext_lazy as _

class ProfileView(DetailView):
    model = Lageruser
    context_object_name = 'profileuser'

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['edits'] = Version.objects.filter(revision__user = context["profileuser"])
        context['devices'] = Device.objects.filter(currentlending__owner = context["profileuser"])
        context["breadcrumbs"] = [("", context["profileuser"])]
        return context


class UsersettingsView(TemplateView):
    template_name = "users/settings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UsersettingsView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['appearanceform'] = AppearanceForm(initial={"pagelength":self.request.user.pagelength})
        context["breadcrumbs"] = [
            (reverse("userprofile", kwargs={"pk":self.request.user.pk}), self.request.user),
            ("", _("Settings"))]
        return context

    def post(self, request):
        print request, request.POST
        if "language" in request.POST:
            request.user.language = request.POST["language"]
            request.user.save()
            request.session['django_language'] =request.POST["language"]
        elif "pagelength" in request.POST:
            if request.user.pagelength != request.POST["pagelength"]:
                request.user.pagelength = request.POST["pagelength"]
                request.user.save()
        return HttpResponseRedirect(reverse("usersettings"))