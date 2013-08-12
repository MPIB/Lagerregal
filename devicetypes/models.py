from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse

class Type(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Type')
        verbose_name_plural = _('Types')

    def get_absolute_url(self):
        return reverse('type-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('type-edit', kwargs={'pk': self.pk})


class TypeAttribute(models.Model):
    devicetype = models.ForeignKey(Type)
    name = models.CharField(max_length=200)
    regex = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = _("Type-attribute")
        verbose_name_plural = _("Type-attributes")

    def get_absolute_url(self):
        return reverse('type-detail', kwargs={'pk': self.devicetype.pk})

    def __unicode__(self):
        return self.name

class TypeAttributeValue(models.Model):
    typeattribute = models.ForeignKey(TypeAttribute)
    value = models.CharField(max_length=400)
    device = models.ForeignKey("devices.Device")

    class Meta:
        verbose_name = _("Type-attribute value")
        verbose_name_plural = _("Type-attribute values")

    def __unicode__(self):
        return self.value
