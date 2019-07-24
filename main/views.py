import datetime

from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from reversion.models import Revision

from devicegroups.models import Devicegroup
from devices.forms import LendForm
from devices.models import Device
from devices.models import Lending
from locations.models import Section
from main.models import WIDGETS
from main.models import DashboardWidget
from main.models import get_progresscolor
from network.models import IpAddress
from users.models import Lageruser


def get_widget_data(user, widgetlist=[], only_user=False):
    context = {}
    context["today"] = datetime.date.today()
    departments = None
    if only_user:
        departments = user.departments.all()
    if "statistics" in widgetlist:
        if departments:
            devices = Device.active().filter(department__in=departments)
        else:
            devices = Device.active()
        context['device_all'] = devices.count()
        if context['device_all'] != 0:
            context['device_available'] = Device.active().filter(currentlending=None).count()
            context["device_percent"] = 100 - int(
                float(context["device_available"]) / context["device_all"] * 100
            )
            context["device_percentcolor"] = get_progresscolor(context["device_percent"])

        context['ipaddress_all'] = IpAddress.objects.all().count()
        if context['ipaddress_all'] != 0:
            context['ipaddress_available'] = IpAddress.objects.filter(device=None).count()
            context["ipaddress_percent"] = 100 - int(
                float(context["ipaddress_available"]) / context["ipaddress_all"] * 100
            )
            context["ipaddress_percentcolor"] = get_progresscolor(context["ipaddress_percent"])
    if "edithistory" in widgetlist:
        if only_user:
            revisions = Revision.objects.filter(user=user)
        else:
            revisions = Revision.objects.all()
        context['revisions'] = (
            revisions
            .select_related('user')
            .prefetch_related('version_set', 'version_set__content_type')
            .order_by("-date_created")[:20]
        )
    if "newestdevices" in widgetlist:
        if departments:
            devices = Device.objects.filter(department__in=departments)
        else:
            devices = Device.objects.all()
        context['newest_devices'] = devices.order_by("-pk")[:10]
    if "overdue" in widgetlist:
        if departments:
            lendings = Lending.objects.select_related("device", "owner").filter(
                Q(device__department__in=departments) | Q(owner__main_department__in=departments)
            )
        else:
            lendings = Lending.objects.select_related("device", "owner")
        context["overdue"] = lendings.filter(duedate__lt=context["today"], returndate=None).order_by("duedate")[:10]
    if "groups" in widgetlist:
        context["groups"] = Devicegroup.objects.all()
    if "sections" in widgetlist:
        context["sections"] = Section.objects.all()
    if "recentlendings" in widgetlist:
        if departments:
            lendings = Lending.objects.select_related("device", "owner").filter(
                Q(device__department__in=departments) | Q(owner__main_department__in=departments)
            )
        else:
            lendings = Lending.objects.select_related("device", "owner")
        context["recentlendings"] = lendings.all().order_by("-pk")[:10]
    if "shorttermdevices" in widgetlist:
        context['shorttermdevices'] = Device.objects.filter(templending=True)[:10]
    if "bookmarks" in widgetlist:
        context["bookmarks"] = user.bookmarks.all()[:10]
    if "returnsoon" in widgetlist:
        soon = context["today"] + datetime.timedelta(days=10)
        if departments:
            lendings = Lending.objects.select_related("device", "owner").filter(
                Q(device__department__in=departments) | Q(owner__main_department__in=departments)
            )
        else:
            lendings = Lending.objects.select_related("device", "owner")
        context["returnsoon"] = lendings.filter(
            duedate__lte=soon,
            duedate__gt=context["today"],
            returndate=None
        ).order_by("duedate")[:10]

    return context


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            context["widgets_left"] = DashboardWidget.objects.filter(user=self.request.user, column="l").order_by("index")
            context["widgets_right"] = DashboardWidget.objects.filter(user=self.request.user, column="r").order_by("index")
            userwidget_list = dict(WIDGETS)
            widgetlist = [x[0] for x in DashboardWidget.objects.filter(user=self.request.user).values_list("widgetname")]
            context.update(get_widget_data(self.request.user, widgetlist, only_user=True))
            for w in context["widgets_left"]:
                if w.widgetname in userwidget_list:
                    del userwidget_list[w.widgetname]
                else:
                    w.delete()

            for w in context["widgets_right"]:
                if w.widgetname in userwidget_list:
                    del userwidget_list[w.widgetname]
                else:
                    w.delete()
            context["widgets_list"] = userwidget_list
            context["lendform"] = LendForm()
            context["lendform"].fields["device"].choices = [
                [device[0], str(device[0]) + " - " + device[1]] for device in (
                    Device
                    .devices_for_departments(self.request.user.departments.all())
                    .filter(trashed=None, currentlending=None, archived=None)
                    .values_list('id', 'name')
                )
            ]
            context["lendform"].fields["device"].choices.insert(0, ["", "---------"])
            context["userlist"] = Lageruser.objects.all().values(
                "pk", "username", "first_name", "last_name")
            context["breadcrumbs"] = [("", _("Dashboard"))]
        else:
            if self.request.user.is_authenticated:
                redirect("userprofile")
        return context
