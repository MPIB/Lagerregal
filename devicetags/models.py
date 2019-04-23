from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from devices.models import Device


# Create your models here.
class Devicetag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    devices = models.ManyToManyField(Device, related_name="tags")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Devicetag')
        verbose_name_plural = _('Devicegtag')
        permissions = (
            ("read_devicetag", _("Can read Devicetag")),
        )

    def get_absolute_url(self):
        return reverse('devicetag-edit', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('devicetag-edit', kwargs={'pk': self.pk})
