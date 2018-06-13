import datetime

from django.views.generic import TemplateView, ListView
from reversion.models import Version, Revision
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from devices.models import *
from network.models import *
from devicegroups.models import Devicegroup
from locations.models import Section
from main.models import DashboardWidget, widgets, get_progresscolor
from Lagerregal.utils import PaginationMixin
from devices.forms import LendForm


def get_widget_data(user, widgetlist=[], departments=None):
    context = {}
    context["today"] = datetime.date.today()
    if "statistics" in widgetlist:
        if departments:
            devices = Device.active().filter(department__in=departments)
        else:
            devices = Device.active()
        context['device_all'] = devices.count()
        if context['device_all'] != 0:
            context['device_available'] = Device.active().filter(currentlending=None).count()
            context["device_percent"] = 100 - int((float(context["device_available"]
                ) / context["device_all"]) * 100)
            context["device_percentcolor"] = get_progresscolor(context["device_percent"])

        context['ipaddress_all'] = IpAddress.objects.all().count()
        if context['ipaddress_all'] != 0:
            context['ipaddress_available'] = IpAddress.objects.filter(device=None).count()
            context["ipaddress_percent"] = 100 - int((float(context["ipaddress_available"]
            ) / context["ipaddress_all"]) * 100)
            context["ipaddress_percentcolor"] = get_progresscolor(context["ipaddress_percent"])
    if "edithistory" in widgetlist:
        context['revisions'] = Revision.objects.select_related("user").prefetch_related("version_set",
                                                                                        "version_set__content_type"
                                                                            ).filter(user__departments__in=departments).order_by("-date_created")[:20]
    if "newestdevices" in widgetlist:
        if departments:
            devices = Device.objects.filter(department__in=departments)
        else:
            devices = Device.objects.all()
        context['newest_devices'] = devices.order_by("-pk")[:10]
    if "overdue" in widgetlist:
        if departments:
            lendings = Lending.objects.select_related("device", "owner").filter(Q(device__department__in=departments) |
                                                                                Q(owner__main_department__in=departments))
        else:
            lendings = Lending.objects.select_related("device", "owner")
        context["overdue"] = lendings.filter(duedate__lt=context["today"], returndate=None).order_by("duedate")[:10]
    if "groups" in widgetlist:
        context["groups"] = Devicegroup.objects.all()
    if "sections" in widgetlist:
        context["sections"] = Section.objects.all()
    if "recentlendings" in widgetlist:
        if departments:
            lendings = Lending.objects.select_related("device", "owner").filter(Q(device__department__in=departments) |
                                                                                Q(owner__main_department__in=departments))
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
            lendings = Lending.objects.select_related("device", "owner").filter(Q(device__department__in=departments) |
                                                                                Q(owner__main_department__in=departments))
        else:
            lendings = Lending.objects.select_related("device", "owner")
        context["returnsoon"] = lendings.filter(duedate__lte=soon, duedate__gt=context["today"],
                                                returndate=None).order_by(
                                                "duedate")[:10]

    return context


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)

        if self.request.user.is_staff:
            context["widgets_left"] = DashboardWidget.objects.filter(user=self.request.user, column="l"
            ).order_by("index")
            context["widgets_right"] = DashboardWidget.objects.filter(user=self.request.user, column="r"
            ).order_by("index")
            userwidget_list = dict(widgets)
            widgetlist = [x[0] for x in DashboardWidget.objects.filter(user=self.request.user
            ).values_list("widgetname")]
            context.update(get_widget_data(self.request.user, widgetlist, self.request.user.departments.all()))
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
            context["lendform"].fields["device"].choices = [[device[0], str(device[0]) + " - " + device[1]] for device
                                                            in Device.devices_for_departments(self.request.user.departments.all()
                                                            ).filter(trashed=None, currentlending=None,
                                                                                     archived=None).values_list('id',
                                                                                                                'name')]
            context["lendform"].fields["device"].choices.insert(0, ["", "---------"])
            context["userlist"] = Lageruser.objects.all().values(
                "pk", "username", "first_name", "last_name")
            context["breadcrumbs"] = [("", _("Dashboard"))]
        else:
            if self.request.user.is_authenticated:
                redirect("userprofile")
        return context


class Globalhistory(PaginationMixin, ListView):
    queryset = Version.objects.select_related("revision", "revision__user", "content_type"
    ).filter().order_by("-pk")
    context_object_name = "revision_list"
    template_name = 'devices/globalhistory.html'

    def get_context_data(self, **kwargs):
        context = super(Globalhistory, self).get_context_data(**kwargs)
        context["breadcrumbs"] = [(reverse("globalhistory"), _("Global edit history"))]
        if context["is_paginated"] and context["page_obj"].number > 1:
            context["breadcrumbs"].append(["", context["page_obj"].number])
        return context
