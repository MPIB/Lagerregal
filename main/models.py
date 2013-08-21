from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Lageruser

widgets = [
    ("edithistory", _("Edit history")),
    ("newestdevices", _("Newest devices")),
    ("overdue", _("Overdue devices")),
    ("statistics", _("Statistics"))
]

class DashboardWidget(models.Model):
    column = models.CharField(max_length=1, choices=[("l", "left"), ("r", "right")])
    index = models.IntegerField()
    widgetname = models.CharField(max_length=200, choices=widgets)
    user = models.ForeignKey(Lageruser)
    minimized = models.BooleanField(default=False)