from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from devices.models import Device
from users.models import Lageruser

# Create your models here.
import reversion


class IpAddress(models.Model):
    address = models.IPAddressField(unique=True)
    device = models.ForeignKey(Device, blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(Lageruser, blank=True, null=True, on_delete=models.SET_NULL)
    last_seen = models.DateTimeField(null=True, blank=True)
    purpose = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.address

    class Meta:
        verbose_name = _('IP-Address')
        verbose_name_plural = _('IP-Addresses')
        permissions = (
            ("read_ipaddress", _("Can read IP-Address")),
        )

    def get_absolute_url(self):
        return reverse('ipaddress-detail', kwargs={'pk': self.pk})


reversion.register(IpAddress, exclude=["last_seen",])
