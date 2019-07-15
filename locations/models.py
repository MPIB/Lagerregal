from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Section(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')

    def get_absolute_url(self):
        return reverse('section-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('section-edit', kwargs={'pk': self.pk})
