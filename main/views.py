from django.views.generic import TemplateView
from devices.models import *
from network.models import *
from reversion.models import Version
import datetime

class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['device_all'] = Device.objects.all().count()
        context['device_available'] = Device.objects.filter(currentlending=None).count()
        context['ipaddress_all'] = IpAddress.objects.all().count()
        context['ipaddress_available'] = IpAddress.objects.filter(device=None).count()
        if self.request.user.is_authenticated():
            context['revisions'] = Version.objects.all().order_by("-pk")[:20]
            context['newest_devices'] = Device.objects.all().order_by("-pk")[:10]
            context["today"] = datetime.date.today()
            context["overdue"] = Device.objects.filter(currentlending__duedate__lt = context["today"]).order_by("currentlending__duedate")
        return context
