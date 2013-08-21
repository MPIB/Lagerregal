from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Lageruser

widgets_list = [
    "edithistory",
    "newestdevices",
    "overdue",
    "statistics"
]

widgets = [
    (widgets_list[0], _("Edit history")),
    (widgets_list[1], _("Newest devices")),
    (widgets_list[2], _("Overdue devices")),
    (widgets_list[3], _("Statistics"))
]

class DashboardWidget(models.Model):
    column = models.CharField(max_length=1, choices=[("l", "left"), ("r", "right")])
    index = models.IntegerField()
    widgetname = models.CharField(max_length=200, choices=widgets)
    user = models.ForeignKey(Lageruser)
    minimized = models.BooleanField(default=False)