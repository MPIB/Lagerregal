from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from reversion import revisions as reversion

from users.models import Department


@reversion.register()
class Devicegroup(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Devicegroup')
        verbose_name_plural = _('Devicegroups')

    def get_absolute_url(self):
        return reverse('devicegroup-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('devicegroup-edit', kwargs={'pk': self.pk})
