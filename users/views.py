from django.views.generic import DetailView, TemplateView
from users.models import Lageruser
from reversion.models import Version
from devices.models import Device
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse

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
        return context


class UsersettingsView(TemplateView):
    template_name = "users/settings.html"

    def post(self, request):
        request.user.language = request.POST["language"]
        request.user.save()
        request.session['django_language'] =request.POST["language"]
        return HttpResponseRedirect(reverse("usersettings"))