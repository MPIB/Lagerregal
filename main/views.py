from django.views.generic import TemplateView, ListView
from devices.models import *
from network.models import *
from devicegroups.models import Devicegroup
from reversion.models import Version
import datetime
from django.contrib.contenttypes.models import ContentType
from main.models import DashboardWidget, widgets, get_progresscolor
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from Lagerregal.utils import PaginationMixin

def get_widget_data():
    context = {}
    context['device_all'] = Device.active().count()
    context['device_available'] = Device.active().filter(currentlending=None).count()
    context["device_percent"] = 100 - int((float(context["device_available"])/context["device_all"])*100)
    context["device_percentcolor"] = get_progresscolor(context["device_percent"] )
    context['ipaddress_all'] = IpAddress.objects.all().count()
    context['ipaddress_available'] = IpAddress.objects.filter(device=None).count()
    context["ipaddress_percent"] = 100 - int((float(context["ipaddress_available"])/context["ipaddress_all"])*100)
    context["ipaddress_percentcolor"] = get_progresscolor(context["ipaddress_percent"] )
    context['revisions'] = Version.objects.select_related("revision", "revision__user", "content_type").filter().order_by("-pk")[:20]
    context['newest_devices'] = Device.objects.select_related().all().order_by("-pk")[:10]
    context["today"] = datetime.date.today()
    context["overdue"] = Device.objects.select_related("currentlending", "currentlending__owner").filter(currentlending__duedate__lt = context["today"]).order_by("currentlending__duedate")[:10]
    context["groups"] = Devicegroup.objects.all()
    context["recentlendings"] = Lending.objects.select_related().all().order_by("-pk")[:10]
    context['shortterm_devices'] = Device.objects.filter(templending=True)[:10]
    return context

class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        if self.request.user.is_staff:
            context.update(get_widget_data())
            context["widgets_left"] = DashboardWidget.objects.filter(user=self.request.user, column="l").order_by("index")
            context["widgets_right"] = DashboardWidget.objects.filter(user=self.request.user, column="r").order_by("index")
            userwidget_list = dict(widgets)
            for w in context["widgets_left"]:
                del userwidget_list[w.widgetname]

            for w in context["widgets_right"]:
                del userwidget_list[w.widgetname]
            context["widgets_list"] = userwidget_list
            context["breadcrumbs"] = [("", _("Dashboard"))]
        else:
            context["breadcrumbs"] = [("", _("Home"))]
            context["form"] = AuthenticationForm()
        return context

class Globalhistory(PaginationMixin, ListView):
    queryset = Version.objects.select_related("revision", "revision__user", "content_type").filter().order_by("-pk")
    context_object_name = "revision_list"
    template_name = 'devices/globalhistory.html'

    def get_context_data(self, **kwargs):
        context = super(Globalhistory, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("globalhistory"), _("Global edit history"))]
        if context["is_paginated"]  and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context
