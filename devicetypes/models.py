from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from reversion import revisions as reversion


@reversion.register()
class Type(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Type')
        verbose_name_plural = _('Types')

    def get_absolute_url(self):
        return reverse('type-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('type-edit', kwargs={'pk': self.pk})


@reversion.register()
class TypeAttribute(models.Model):
    devicetype = models.ForeignKey(Type, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    regex = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = _("Type-attribute")
        verbose_name_plural = _("Type-attributes")

    def get_absolute_url(self):
        return reverse('type-detail', kwargs={'pk': self.devicetype.pk})

    def __str__(self):
        return self.name


@reversion.register()
class TypeAttributeValue(models.Model):
    typeattribute = models.ForeignKey(TypeAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=400)
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Type-attribute value")
        verbose_name_plural = _("Type-attribute values")

    def __str__(self):
        return self.value
