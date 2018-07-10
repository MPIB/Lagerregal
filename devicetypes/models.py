from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

import six
from reversion import revisions as reversion


@six.python_2_unicode_compatible
class Type(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Type')
        verbose_name_plural = _('Types')
        permissions = (
            ("read_type", _("Can read Type")),
        )

    def get_absolute_url(self):
        return reverse('type-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('type-edit', kwargs={'pk': self.pk})


@six.python_2_unicode_compatible
class TypeAttribute(models.Model):
    devicetype = models.ForeignKey(Type)
    name = models.CharField(max_length=200)
    regex = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = _("Type-attribute")
        verbose_name_plural = _("Type-attributes")

    def get_absolute_url(self):
        return reverse('type-detail', kwargs={'pk': self.devicetype.pk})

    def __str__(self):
        return self.name


@six.python_2_unicode_compatible
class TypeAttributeValue(models.Model):
    typeattribute = models.ForeignKey(TypeAttribute)
    value = models.CharField(max_length=400)
    device = models.ForeignKey("devices.Device")

    class Meta:
        verbose_name = _("Type-attribute value")
        verbose_name_plural = _("Type-attribute values")

    def __str__(self):
        return self.value


reversion.register(Type)
reversion.register(TypeAttribute)
