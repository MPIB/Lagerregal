from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from users.models import Lageruser

WIDGETS = [
    ("edithistory", _("Edit history")),
    ("newestdevices", _("Newest devices")),
    ("overdue", _("Overdue devices")),
    ("statistics", _("Statistics")),
    ("groups", _("Groups")),
    ("sections", _("Sections")),
    ("recentlendings", _("Recent lendings")),
    ("shorttermdevices", _("Devices for short term lending")),
    ("bookmarks", _("Bookmarked Devices")),
    ("returnsoon", _("Devices, that are due soon")),
]


def get_progresscolor(percent):
    if percent > 90:
        return "danger"
    elif percent > 60:
        return "warning"
    else:
        return "success"


class DashboardWidget(models.Model):
    column = models.CharField(max_length=1, choices=[("l", "left"), ("r", "right")])
    index = models.IntegerField()
    widgetname = models.CharField(max_length=200, choices=WIDGETS)
    user = models.ForeignKey(Lageruser, on_delete=models.CASCADE)
    minimized = models.BooleanField(default=False)


def create_dashboard(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        DashboardWidget(column="l", index=0, widgetname="statistics", user=instance, minimized=False).save()
        DashboardWidget(column="l", index=1, widgetname="newestdevices", user=instance, minimized=False).save()
        DashboardWidget(column="l", index=2, widgetname="overdue", user=instance, minimized=False).save()
        DashboardWidget(column="r", index=0, widgetname="bookmarks", user=instance, minimized=False).save()
        DashboardWidget(column="r", index=0, widgetname="edithistory", user=instance, minimized=False).save()


post_save.connect(create_dashboard, sender=Lageruser)
