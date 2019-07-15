from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from reversion import revisions as reversion

from devices.models import Device
from users.models import Department
from users.models import Lageruser


@reversion.register(exclude=["last_seen"])
class IpAddress(models.Model):
    address = models.GenericIPAddressField(unique=True)
    device = models.ForeignKey(Device, blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(Lageruser, blank=True, null=True, on_delete=models.SET_NULL)
    last_seen = models.DateTimeField(null=True, blank=True)
    purpose = models.CharField(max_length=200, null=True, blank=True)
    # an IP that does not belong to a department is considered public
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = _('IP-Address')
        verbose_name_plural = _('IP-Addresses')
        ordering = ['address']

    def get_absolute_url(self):
        return reverse('ipaddress-detail', kwargs={'pk': self.pk})
