from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

import six
from reversion import revisions as reversion

from devices.models import Device
from users.models import Department, Lageruser


@six.python_2_unicode_compatible
class IpAddress(models.Model):
    address = models.GenericIPAddressField(unique=True)
    device = models.ForeignKey(Device, blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(Lageruser, blank=True, null=True, on_delete=models.SET_NULL)
    last_seen = models.DateTimeField(null=True, blank=True)
    purpose = models.CharField(max_length=200, null=True, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = _('IP-Address')
        verbose_name_plural = _('IP-Addresses')
        permissions = (
            ("read_ipaddress", _("Can read IP-Address")),
        )

    def get_absolute_url(self):
        return reverse('ipaddress-detail', kwargs={'pk': self.pk})


reversion.register(IpAddress, exclude=["last_seen"])
