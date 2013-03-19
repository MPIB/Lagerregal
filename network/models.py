from django.db import models
from devices.models import Device
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
# Create your models here.

class IpAddress(models.Model):
	address = models.IPAddressField(unique=True)
	device = models.ForeignKey(Device, blank=True, null=True)

	def __unicode__(self):
		return self.address

	class Meta:
		verbose_name = _('IP-Address')
		verbose_name_plural = _('IP-Addresses')

	def get_absolute_url(self):
		return reverse('ipaddress-detail', kwargs={'pk': self.pk})