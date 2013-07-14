from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from reversion.models import Version

class ProfileView(DetailView):
    model = User
    context_object_name = 'user'

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['edits'] = Version.objects.filter(revision__user = self.request.user)
        return context